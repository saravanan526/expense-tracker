import mysql.connector
import streamlit as st

# set_page_config must be the FIRST Streamlit command, and only called once
st.set_page_config(page_title="Expense Tracker", page_icon="💰", layout="wide")

import auth
import auth_ui
import dashboard_ui
import database as db
from pages import add_expense, analytics, budget, expense_history, home

# ---------------------------------------------------------------------
# Not logged in -> styled login / register screen
# ---------------------------------------------------------------------
def login_page():
    auth_ui.apply_theme()
    auth_ui.render_auth_page()


if not auth.is_logged_in():
    # A login-only navigation replaces the old page URL (e.g. /budget)
    # so the address bar goes back to the root after logout.
    st.navigation(
        [st.Page(login_page, title="Login", url_path="login", default=True)],
        position="hidden",
    ).run()
    st.stop()

# ---------------------------------------------------------------------
# Logged in -> dashboard theme
# ---------------------------------------------------------------------
dashboard_ui.apply_dashboard_theme()

# Connect to MySQL and create the tables (only once per session)
if "db_ready" not in st.session_state:
    try:
        db.setup_database()
        st.session_state["db_ready"] = True
    except mysql.connector.Error as error:
        st.error("Could not connect to MySQL. Check that MySQL is running "
                 "and that the details in your .env file are correct.")
        st.code(str(error))
        st.stop()


def run_page(page_function):
    """Run a page and show a simple message if a database error happens."""
    try:
        page_function()
    except mysql.connector.Error as error:
        st.error("A database error occurred. Please check the MySQL connection.")
        st.code(str(error))


def home_page():
    run_page(home.show)


def add_expense_page():
    run_page(add_expense.show)


def history_page():
    run_page(expense_history.show)


def analytics_page():
    run_page(analytics.show)


def budget_page():
    run_page(budget.show)


pages = [
    st.Page(home_page, title="Home", icon="🏠", url_path="home", default=True),
    st.Page(add_expense_page, title="Add Expense", icon="➕", url_path="add-expense"),
    st.Page(history_page, title="Expense History", icon="🧾", url_path="expense-history"),
    st.Page(analytics_page, title="Analytics", icon="📊", url_path="analytics"),
    st.Page(budget_page, title="Budget Analysis", icon="🎯", url_path="budget"),
]
navigation = st.navigation(pages)

dashboard_ui.sidebar_brand()
auth_ui.render_sidebar_user()      # user card + Log out button

navigation.run()