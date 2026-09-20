"""
database.py
-----------
All MySQL code is kept in this one file:
  * connection
  * table creation (and upgrade of old tables)
  * SQL queries (SELECT, INSERT, UPDATE, DELETE)

Every query that uses user input is parameterized (%s) to avoid SQL injection.
Every expense / budget / recurring query also filters by user_id, so each
user can only see his or her own data.
"""

import os

import mysql.connector
import pandas as pd
from dotenv import load_dotenv

# Read DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME from the .env file
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))      # cloud databases use their own port
DB_SSL_CA = os.getenv("DB_SSL_CA")     # optional: path to the CA certificate file
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_NAME = os.getenv("DB_NAME", "expense_tracker_db")

# Values used in the dropdowns of the app
CATEGORIES = ["Food", "Transport", "Shopping", "Education", "Bills", "Entertainment", "Other"]
PAYMENT_METHODS = ["Cash", "UPI", "Debit Card", "Credit Card", "Bank Transfer"]
FREQUENCIES = ["Weekly", "Monthly", "Yearly"]

# ---------------------------------------------------------------------
# Table creation queries
# ---------------------------------------------------------------------
CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_EXPENSES = """
CREATE TABLE IF NOT EXISTS expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    expense_date DATE NOT NULL,
    category VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    description VARCHAR(255),
    CONSTRAINT fk_expenses_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
"""

CREATE_BUDGETS = """
CREATE TABLE IF NOT EXISTS budgets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    month_year VARCHAR(7) NOT NULL,
    budget_amount DECIMAL(10,2) NOT NULL,
    UNIQUE KEY unique_user_month (user_id, month_year),
    CONSTRAINT fk_budgets_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
"""

CREATE_RECURRING = """
CREATE TABLE IF NOT EXISTS recurring_expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    expense_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    amount DECIMAL(10,2) NOT NULL,
    due_day INT,
    frequency VARCHAR(20),
    CONSTRAINT fk_recurring_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
"""


# ---------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------
def get_connection(with_database=True):
    """Open a new MySQL connection. Raises mysql.connector.Error on failure."""
    config = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PASSWORD,
    }

    if with_database:
        config["database"] = DB_NAME

    if DB_SSL_CA:
        config["ssl_ca"] = DB_SSL_CA

    return mysql.connector.connect(**config)
    config["use_pure"] = True


def _column_exists(cursor, table, column):
    cursor.execute(
        "SELECT COUNT(*) FROM information_schema.columns "
        "WHERE table_schema = %s AND table_name = %s AND column_name = %s",
        (DB_NAME, table, column),
    )
    return cursor.fetchone()[0] > 0


def _index_exists(cursor, table, index_name):
    cursor.execute(
        "SELECT COUNT(*) FROM information_schema.statistics "
        "WHERE table_schema = %s AND table_name = %s AND index_name = %s",
        (DB_NAME, table, index_name),
    )
    return cursor.fetchone()[0] > 0


def _upgrade_old_tables(cursor):
    """
    Projects created before the login feature have no user_id column.
    This adds the column (and the foreign key) to those old tables.
    Old rows keep user_id = NULL and are given to the first registered user.
    """
    for table, fk_name in (("expenses", "fk_expenses_user"),
                           ("budgets", "fk_budgets_user"),
                           ("recurring_expenses", "fk_recurring_user")):
        if not _column_exists(cursor, table, "user_id"):
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN user_id INT NULL")
            cursor.execute(
                f"ALTER TABLE {table} ADD CONSTRAINT {fk_name} "
                f"FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE"
            )

    # Old budgets table: month_year was UNIQUE. Now it is unique per user.
    if not _index_exists(cursor, "budgets", "unique_user_month"):
        cursor.execute("ALTER TABLE budgets ADD UNIQUE KEY unique_user_month (user_id, month_year)")
    if _index_exists(cursor, "budgets", "month_year"):
        cursor.execute("ALTER TABLE budgets DROP INDEX month_year")


def setup_database():
    """Create the tables (and the database too, if it does not exist)."""
    try:
        conn = get_connection()                      # cloud DB already exists
    except mysql.connector.Error as error:
        if error.errno != 1049:                      # 1049 = unknown database
            raise
        first = get_connection(with_database=False)  # local MySQL, first run
        cur = first.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
        first.commit()
        cur.close()
        first.close()
        conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(CREATE_USERS)          # users must be created first (foreign key)
        cursor.execute(CREATE_EXPENSES)
        cursor.execute(CREATE_BUDGETS)
        cursor.execute(CREATE_RECURRING)
        _upgrade_old_tables(cursor)
        conn.commit()
        cursor.close()
    finally:
        conn.close()


def run_select(query, params=None):
    """Run a SELECT query and return the result as a Pandas DataFrame."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        columns = cursor.column_names
        cursor.close()
    finally:
        conn.close()

    df = pd.DataFrame(rows, columns=columns)

    # MySQL returns DECIMAL values as Decimal objects. Convert them to float.
    for col in ("amount", "total", "budget_amount"):
        if col in df.columns:
            df[col] = df[col].astype(float)
    return df


def run_change(query, params=None):
    """Run an INSERT / UPDATE / DELETE query. Returns the id of the inserted row."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
    finally:
        conn.close()
    return new_id


# ---------------------------------------------------------------------
# Users table
# ---------------------------------------------------------------------
def count_users():
    df = run_select("SELECT COUNT(*) AS total_users FROM users")
    return int(df.iloc[0]["total_users"])


def username_exists(username):
    df = run_select("SELECT id FROM users WHERE username = %s", (username,))
    return not df.empty


def email_exists(email):
    df = run_select("SELECT id FROM users WHERE email = %s", (email,))
    return not df.empty


def get_user_by_username(username):
    """Return the user as a dictionary, or None if the username does not exist."""
    df = run_select(
        "SELECT id, full_name, username, email, password_hash FROM users WHERE username = %s",
        (username,),
    )
    if df.empty:
        return None
    row = df.iloc[0]
    return {
        "id": int(row["id"]),
        "full_name": row["full_name"],
        "username": row["username"],
        "email": row["email"],
        "password_hash": row["password_hash"],
    }


def create_user(full_name, username, email, password_hash):
    """Insert a new user and return the new user id."""
    query = """
        INSERT INTO users (full_name, username, email, password_hash)
        VALUES (%s, %s, %s, %s)
    """
    user_id = run_change(query, (full_name, username, email, password_hash))

    # The very first user gets the data that existed before the login feature was added
    if count_users() == 1:
        assign_old_records(user_id)
    return user_id


def assign_old_records(user_id):
    for table in ("expenses", "budgets", "recurring_expenses"):
        run_change(f"UPDATE {table} SET user_id = %s WHERE user_id IS NULL", (user_id,))


# ---------------------------------------------------------------------
# Expenses table
# ---------------------------------------------------------------------
def insert_expense(user_id, expense_date, category, amount, payment_method, description):
    query = """
        INSERT INTO expenses (user_id, expense_date, category, amount, payment_method, description)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    run_change(query, (user_id, expense_date, category, amount, payment_method, description))


def _build_where(user_id, start_date=None, end_date=None, category=None, payment_method=None):
    """Build the WHERE part of the query from the logged-in user and the selected filters."""
    conditions = ["user_id = %s"]
    params = [user_id]

    if start_date and end_date:
        conditions.append("expense_date BETWEEN %s AND %s")
        params.extend([start_date, end_date])
    elif start_date:
        conditions.append("expense_date >= %s")
        params.append(start_date)
    elif end_date:
        conditions.append("expense_date <= %s")
        params.append(end_date)

    if category:
        conditions.append("category = %s")
        params.append(category)

    if payment_method:
        conditions.append("payment_method = %s")
        params.append(payment_method)

    return " WHERE " + " AND ".join(conditions), params


def get_expenses(user_id, start_date=None, end_date=None, category=None, payment_method=None):
    """Return the user's expenses (newest first). All filters are optional."""
    where, params = _build_where(user_id, start_date, end_date, category, payment_method)
    query = (
        "SELECT id, expense_date, category, amount, payment_method, description "
        "FROM expenses" + where + " ORDER BY expense_date DESC, id DESC"
    )
    return run_select(query, params)


def get_filtered_stats(user_id, start_date=None, end_date=None, category=None, payment_method=None):
    """SUM, COUNT, AVG and MAX of the (filtered) expenses."""
    where, params = _build_where(user_id, start_date, end_date, category, payment_method)
    query = (
        "SELECT COALESCE(SUM(amount), 0) AS total, COUNT(*) AS num_transactions, "
        "COALESCE(AVG(amount), 0) AS average, COALESCE(MAX(amount), 0) AS highest "
        "FROM expenses" + where
    )
    df = run_select(query, params)
    row = df.iloc[0]
    return {
        "total": float(row["total"]),
        "count": int(row["num_transactions"]),
        "average": float(row["average"]),
        "highest": float(row["highest"]),
    }


def get_recent_expenses(user_id, limit=5):
    """Latest expenses (uses ORDER BY and LIMIT)."""
    query = (
        "SELECT id, expense_date, category, amount, payment_method, description "
        "FROM expenses WHERE user_id = %s ORDER BY expense_date DESC, id DESC LIMIT %s"
    )
    return run_select(query, (user_id, limit))


def get_date_range(user_id):
    """Return (first expense date, last expense date). (None, None) if no data."""
    df = run_select(
        "SELECT MIN(expense_date) AS first_date, MAX(expense_date) AS last_date "
        "FROM expenses WHERE user_id = %s", (user_id,))
    first_date = df.iloc[0]["first_date"]
    last_date = df.iloc[0]["last_date"]
    if pd.isna(first_date) or pd.isna(last_date):
        return None, None
    return first_date, last_date


# ---------------------------------------------------------------------
# Month-wise queries (MONTH() and YEAR())
# ---------------------------------------------------------------------
def _month_filter(user_id, year=None, month=None):
    """WHERE part: the user's rows, and optionally one month only."""
    where = " WHERE user_id = %s"
    params = [user_id]
    if year is not None and month is not None:
        where += " AND YEAR(expense_date) = %s AND MONTH(expense_date) = %s"
        params.extend([year, month])
    return where, params


def get_month_expenses(user_id, year, month):
    where, params = _month_filter(user_id, year, month)
    query = (
        "SELECT id, expense_date, category, amount, payment_method, description "
        "FROM expenses" + where + " ORDER BY expense_date"
    )
    return run_select(query, params)


def get_month_stats(user_id, year, month):
    """Total and number of transactions for one month."""
    where, params = _month_filter(user_id, year, month)
    query = (
        "SELECT COALESCE(SUM(amount), 0) AS total, COUNT(*) AS num_transactions "
        "FROM expenses" + where
    )
    df = run_select(query, params)
    return {
        "total": float(df.iloc[0]["total"]),
        "count": int(df.iloc[0]["num_transactions"]),
    }


def get_category_totals(user_id, year=None, month=None):
    where, params = _month_filter(user_id, year, month)
    query = (
        "SELECT category, SUM(amount) AS total FROM expenses" + where +
        " GROUP BY category ORDER BY total DESC"
    )
    return run_select(query, params)


def get_payment_totals(user_id, year=None, month=None):
    where, params = _month_filter(user_id, year, month)
    query = (
        "SELECT payment_method, SUM(amount) AS total FROM expenses" + where +
        " GROUP BY payment_method ORDER BY total DESC"
    )
    return run_select(query, params)


def get_daily_totals(user_id, year=None, month=None):
    where, params = _month_filter(user_id, year, month)
    query = (
        "SELECT expense_date, SUM(amount) AS total FROM expenses" + where +
        " GROUP BY expense_date ORDER BY expense_date"
    )
    return run_select(query, params)


def get_monthly_totals(user_id):
    query = (
        "SELECT YEAR(expense_date) AS year, MONTH(expense_date) AS month, SUM(amount) AS total "
        "FROM expenses WHERE user_id = %s "
        "GROUP BY YEAR(expense_date), MONTH(expense_date) "
        "ORDER BY year, month"
    )
    return run_select(query, (user_id,))


# ---------------------------------------------------------------------
# Budgets table
# ---------------------------------------------------------------------
def save_budget(user_id, month_year, budget_amount):
    """Insert a budget, or update it if this user already has a budget for the month."""
    query = """
        INSERT INTO budgets (user_id, month_year, budget_amount)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE budget_amount = VALUES(budget_amount)
    """
    run_change(query, (user_id, month_year, budget_amount))


def get_budget(user_id, month_year):
    """Return the budget of a month as float, or None if not set."""
    df = run_select(
        "SELECT budget_amount FROM budgets WHERE user_id = %s AND month_year = %s",
        (user_id, month_year))
    if df.empty:
        return None
    return float(df.iloc[0]["budget_amount"])


def get_all_budgets(user_id):
    query = (
        "SELECT month_year, budget_amount FROM budgets "
        "WHERE user_id = %s ORDER BY month_year DESC LIMIT 12"
    )
    return run_select(query, (user_id,))


# ---------------------------------------------------------------------
# Recurring expenses table
# ---------------------------------------------------------------------
def add_recurring_expense(user_id, expense_name, category, amount, due_day, frequency):
    query = """
        INSERT INTO recurring_expenses (user_id, expense_name, category, amount, due_day, frequency)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    run_change(query, (user_id, expense_name, category, amount, due_day, frequency))


def get_recurring_expenses(user_id):
    query = (
        "SELECT id, expense_name, category, amount, due_day, frequency "
        "FROM recurring_expenses WHERE user_id = %s ORDER BY id"
    )
    return run_select(query, (user_id,))


def delete_recurring_expense(user_id, recurring_id):
    run_change("DELETE FROM recurring_expenses WHERE id = %s AND user_id = %s",
               (recurring_id, user_id))


# ---------------------------------------------------------------------
# Sample data import
# ---------------------------------------------------------------------
def import_expenses_from_csv(user_id, csv_path):
    """Insert all rows of a CSV file into the expenses table. Returns row count."""
    df = pd.read_csv(csv_path)
    df["description"] = df["description"].fillna("")

    rows = []
    for _, row in df.iterrows():
        rows.append((
            user_id,
            row["expense_date"],
            row["category"],
            float(row["amount"]),
            row["payment_method"],
            row["description"],
        ))

    query = """
        INSERT INTO expenses (user_id, expense_date, category, amount, payment_method, description)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.executemany(query, rows)
        conn.commit()
        cursor.close()
    finally:
        conn.close()
    return len(rows)
