# Expense Tracker and Data Analytics Dashboard

A college mini project built with **Python, Streamlit, MySQL, SQL, Pandas, Matplotlib and a REST API**.
Users can record daily expenses, store them in MySQL, and analyze their spending with SQL queries,
Pandas calculations and simple Matplotlib charts.

## Features

**User registration and login:** every user creates an account and sees only his or her own data. Passwords are stored as salted PBKDF2 hashes (Python `hashlib`), never as plain text.

| Page | What it does |
|---|---|
| Login / Register | Create an account or login (shown before logging in) |
| Home | Total expense, this month's expense, number of transactions, average expense, rule-based spending summary, recent expenses |
| Add Expense | Form with validation (amount > 0, required fields, valid date), stores data in MySQL |
| Expense History | Table of expenses, filters (date range, category, payment method), statistics of the filtered data, CSV download |
| Analytics | Category-wise bar chart, monthly line chart, payment-method bar chart, daily trend line chart, fixed vs variable analysis |
| Budget Analysis | Monthly budget with utilization status, current vs previous month comparison, recurring expenses, currency converter |

## Technology Used

- Python 3.9+
- Streamlit (user interface)
- MySQL + SQL (database)
- Pandas (data cleaning, grouping, aggregation, CSV export)
- Matplotlib (charts)
- Requests (currency exchange REST API)
- python-dotenv (database credentials in a `.env` file)

No machine learning or AI is used. All summaries are rule-based Python calculations.

## Project Structure

```text
expense_tracker/
├── app.py                  # Main file, sidebar navigation
├── database.py             # MySQL connection and all SQL queries
├── api.py                  # Currency converter (REST API)
├── auth.py                 # Registration, login, password hashing
├── analysis.py             # Pandas calculations, summary, Matplotlib charts
├── requirements.txt
├── README.md
├── PROJECT_GUIDE.md        # Explanation, interview questions, resume text
├── .env.example
├── style.css               # Custom CSS styling (metric boxes, buttons, forms)
├── .streamlit/config.toml  # Light theme colors
├── pages/
│   ├── login.py            # Login / Register page
│   ├── home.py
│   ├── add_expense.py
│   ├── expense_history.py
│   ├── analytics.py
│   └── budget.py           # Budget, comparison, recurring expenses, currency
├── sql/
│   └── database.sql
└── data/
    └── sample_expenses.csv
```

## Database Tables

- `users` - registered users (username, email, password hash)
- `expenses` - daily (variable) expenses, each row has a `user_id`
- `budgets` - one budget per user per month (`month_year` like `2026-09`)
- `recurring_expenses` - fixed expenses such as rent and internet, each row has a `user_id`

`expenses`, `budgets` and `recurring_expenses` are linked to `users` with a FOREIGN KEY on `user_id`. Every query has `WHERE user_id = %s`, so users never see each other's data.

SQL concepts used: SELECT, WHERE, BETWEEN, GROUP BY, ORDER BY, LIMIT, SUM, AVG, COUNT, MAX, MIN,
MONTH(), YEAR(), INSERT ... ON DUPLICATE KEY UPDATE, parameterized queries.

## How to Run

1. **Install Python** (3.9 or above) and **MySQL Server**. Make sure MySQL is running.

2. **Open the project folder** in a terminal:
   ```bash
   cd expense_tracker
   ```

3. **Create a virtual environment** (recommended) and install packages:
   ```bash
   python -m venv venv
   venv\Scripts\activate          # Windows
   source venv/bin/activate       # Linux / Mac
   pip install -r requirements.txt
   ```

4. **Create the `.env` file**: copy `.env.example` to `.env` and write your MySQL details:
   ```text
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_NAME=expense_tracker_db
   ```

5. **Run the app**:
   ```bash
   streamlit run app.py
   ```
   The database and tables are created automatically on the first run.
   (You can also run `sql/database.sql` manually in MySQL Workbench.)

6. **Register**: on the first screen open the *Register* tab, create an account, then login from the *Login* tab.

7. **Load sample data**: open *Add Expense* page and click **Load Sample Data**
   (40 records from July to September 2026, added to your account).

**Already using the older version (without login)?** Just run the new version. The app adds the `user_id` columns to your old tables automatically, and your old expenses, budgets and recurring expenses are given to the **first account you register**. If the upgrade fails for any reason, drop the database (`DROP DATABASE expense_tracker_db;`) and start again.

**Note:** Streamlit keeps the login only for the open browser tab. If you refresh the page (F5) you must login again.

## Formulas Used

```text
Remaining          = Budget - Spent
Utilization        = (Spent / Budget) x 100
Difference         = Current Month - Previous Month
Percentage Change  = (Difference / Previous Month) x 100
Fixed %            = Fixed / (Fixed + Variable) x 100
Variable %         = Variable / (Fixed + Variable) x 100
```

Budget rules: below 80% = Normal spending, 80-100% = Budget nearing limit, above 100% = Budget exceeded.

Fixed expenses are the recurring expenses converted to a monthly amount
(weekly x 52 / 12, monthly x 1, yearly / 12). Variable expenses are the normal daily expenses of the month.

## Common Errors and Fixes

| Error | Fix |
|---|---|
| `Could not connect to MySQL` / `Access denied` | Check that MySQL is running and `DB_USER` / `DB_PASSWORD` in `.env` are correct |
| `Unknown database` | Not an issue normally (app creates it). If it appears, run `sql/database.sql` once |
| `ModuleNotFoundError` | Activate the virtual environment and run `pip install -r requirements.txt` |
| `AttributeError: module 'streamlit' has no attribute 'Page'` | Upgrade Streamlit: `pip install --upgrade streamlit` (version 1.36 or above is needed) |
| `This username is already taken` | Choose a different username (usernames are not case-sensitive) |
| Cannot login after refreshing the page | Normal for Streamlit; login again |
| Currency converter shows an error | Check the internet connection and try again |
| `Authentication plugin 'caching_sha2_password'` | Update `mysql-connector-python`, or use a MySQL user with `mysql_native_password` |

## Future Enhancements

- Stay logged in after page refresh (cookies), password reset by email
- Limit wrong password attempts
- Edit and delete expenses
- Category-wise budgets
- Export charts as images or PDF
- Deploy the app on Streamlit Cloud with a cloud MySQL database


### UI Styling
The project uses `style.css` for a colorful blue-purple dashboard theme, cards, buttons, sidebar and form styling.
