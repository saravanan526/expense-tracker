"""Add Expense page: form with validation + sample data import."""

import os
from datetime import date

import streamlit as st

import auth
import database as db

SAMPLE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample_expenses.csv")
MAX_AMOUNT = 99999999.99   # limit of DECIMAL(10,2)


def show():
    user_id = auth.get_user_id()
    st.title("Add Expense")

    with st.form("expense_form"):
        expense_date = st.date_input("Date", value=date.today())
        category = st.selectbox("Category", db.CATEGORIES)
        amount = st.number_input("Amount (₹)", min_value=0.0, value=None,
                                 step=1.0, format="%.2f", placeholder="Enter amount")
        payment_method = st.selectbox("Payment Method", db.PAYMENT_METHODS)
        description = st.text_input("Description", max_chars=255)
        submitted = st.form_submit_button("Add Expense")

    if submitted:
        errors = validate_expense(expense_date, category, amount, payment_method, description)
        if errors:
            for message in errors:
                st.error(message)
        else:
            db.insert_expense(user_id, expense_date, category, amount, payment_method, description.strip())
            st.success("Expense added successfully.")

    # ---- Sample data (only when the table is empty) ----
    st.divider()
    st.subheader("Sample Data")
    st.write("Load 40 sample expense records (July - September 2026) to test the project.")

    if st.button("Load Sample Data"):
        if db.get_filtered_stats(user_id)["count"] > 0:
            st.warning("Sample data can only be loaded when you have no expenses.")
        elif not os.path.exists(SAMPLE_FILE):
            st.error("Sample file data/sample_expenses.csv was not found.")
        else:
            count = db.import_expenses_from_csv(user_id, SAMPLE_FILE)
            st.success(f"{count} sample records loaded. Open the Home page to see them.")


def validate_expense(expense_date, category, amount, payment_method, description):
    """Return a list of error messages (empty list = everything is valid)."""
    errors = []

    if not isinstance(expense_date, date):
        errors.append("Please select a valid date.")
    elif expense_date > date.today():
        errors.append("Date cannot be in the future.")

    if not category:
        errors.append("Category is required.")
    if not payment_method:
        errors.append("Payment method is required.")

    if amount is None:
        errors.append("Amount cannot be empty.")
    elif amount <= 0:
        errors.append("Amount must be greater than 0.")
    elif amount > MAX_AMOUNT:
        errors.append("Amount is too large.")

    if not description or not description.strip():
        errors.append("Description cannot be empty.")

    return errors
