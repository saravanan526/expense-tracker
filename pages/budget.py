"""
Budget Analysis page with four sections:
  1. Monthly Budget          (Feature 2)
  2. Monthly Comparison      (Feature 3)
  3. Recurring Expenses      (Feature 4)
  4. Currency Converter      (REST API)
"""

import calendar
from datetime import date

import matplotlib.pyplot as plt
import streamlit as st

import analysis as an
import api
import auth
import database as db


def month_selector(key_prefix):
    """Two boxes to choose year and month. Returns (year, month)."""
    today = date.today()
    col1, col2 = st.columns(2)
    year = col1.number_input("Year", min_value=2000, max_value=2100, value=today.year,
                             step=1, key=key_prefix + "_year")
    month = col2.selectbox("Month", list(range(1, 13)), index=today.month - 1,
                           format_func=lambda m: calendar.month_name[m],
                           key=key_prefix + "_month")
    return int(year), int(month)


def show():
    st.title("Budget Analysis")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Monthly Budget", "Monthly Comparison", "Recurring Expenses", "Currency Converter"]
    )
    with tab1:
        show_budget()
    with tab2:
        show_comparison()
    with tab3:
        show_recurring()
    with tab4:
        show_currency()


# ---------------------------------------------------------------------
# Feature 2 - Monthly budget
# ---------------------------------------------------------------------
def show_budget():
    user_id = auth.get_user_id()
    st.subheader("Monthly Budget")
    year, month = month_selector("budget")
    month_year = f"{year}-{month:02d}"          # example: 2026-09

    saved_budget = db.get_budget(user_id, month_year)
    new_budget = st.number_input("Budget amount (₹)", min_value=0.0, step=500.0,
                                 value=saved_budget if saved_budget else 10000.0,
                                 format="%.2f", key="budget_input_" + month_year)

    if st.button("Save Budget"):
        if new_budget <= 0:
            st.error("Budget must be greater than 0.")
        else:
            db.save_budget(user_id, month_year, new_budget)
            st.success("Budget saved.")
            saved_budget = new_budget

    if saved_budget is None:
        st.info("No budget is set for this month. Enter an amount and click 'Save Budget'.")
        return

    spent = db.get_month_stats(user_id, year, month)["total"]
    result = an.calculate_budget_status(saved_budget, spent)
    if result is None:
        st.error("Budget is zero, so utilization cannot be calculated.")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Budget", an.format_inr(result["budget"]))
    c2.metric("Spent", an.format_inr(result["spent"]))
    c3.metric("Remaining", an.format_inr(result["remaining"]))
    c4.metric("Utilization", f"{result['utilization']:.1f}%")

    st.progress(min(result["utilization"] / 100, 1.0))

    if result["level"] == "ok":
        st.success(result["status"])
    elif result["level"] == "warning":
        st.warning(result["status"])
    else:
        st.error(result["status"])

    all_budgets = db.get_all_budgets(user_id)
    if not all_budgets.empty:
        st.write("Saved budgets:")
        st.dataframe(all_budgets.rename(columns={
            "month_year": "Month", "budget_amount": "Budget"}), hide_index=True)


# ---------------------------------------------------------------------
# Feature 3 - Current month vs previous month
# ---------------------------------------------------------------------
def show_comparison():
    user_id = auth.get_user_id()
    st.subheader("Current Month vs Previous Month")
    year, month = month_selector("compare")
    prev_year, prev_month = an.previous_month(year, month)

    current = db.get_month_stats(user_id, year, month)
    previous = db.get_month_stats(user_id, prev_year, prev_month)

    if current["count"] == 0:
        st.warning("No expenses found for the selected month.")
        return

    result = an.compare_months(current["total"], previous["total"], previous["count"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current Month", an.format_inr(result["current"]))
    c2.metric("Previous Month", an.format_inr(result["previous"]))
    c3.metric("Difference", an.format_inr(result["difference"]))
    if result["percent"] is None:
        c4.metric("Percentage Change", "N/A")
        st.info(result["message"])
    else:
        c4.metric("Percentage Change", f"{result['percent']:.1f}%")
        st.write(result["message"])

    fig = an.comparison_chart(an.month_label(prev_year, prev_month), result["previous"],
                              an.month_label(year, month), result["current"])
    st.pyplot(fig)
    plt.close(fig)


# ---------------------------------------------------------------------
# Feature 4 - Recurring expenses
# ---------------------------------------------------------------------
def show_recurring():
    user_id = auth.get_user_id()
    st.subheader("Recurring Expenses")
    st.write("Examples: Rent, Internet, Mobile Recharge, Subscription, Electricity.")

    with st.form("recurring_form"):
        name = st.text_input("Expense name", max_chars=100)
        category = st.selectbox("Category", db.CATEGORIES)
        amount = st.number_input("Amount (₹)", min_value=0.0, value=None, step=1.0,
                                 format="%.2f", placeholder="Enter amount")
        due_day = st.number_input("Due day (1 - 31)", min_value=1, max_value=31, value=1, step=1)
        frequency = st.selectbox("Frequency", db.FREQUENCIES, index=1)
        submitted = st.form_submit_button("Add Recurring Expense")

    if submitted:
        if not name.strip():
            st.error("Expense name cannot be empty.")
        elif amount is None or amount <= 0:
            st.error("Amount must be greater than 0.")
        else:
            db.add_recurring_expense(user_id, name.strip(), category, amount, int(due_day), frequency)
            st.success("Recurring expense added.")

    recurring = db.get_recurring_expenses(user_id)
    if recurring.empty:
        st.info("No recurring expenses added yet.")
        return

    recurring = an.add_monthly_amount(recurring)
    table = recurring.rename(columns={
        "id": "ID", "expense_name": "Expense Name", "category": "Category",
        "amount": "Amount", "due_day": "Due Day", "frequency": "Frequency",
        "monthly_amount": "Monthly Amount"})
    st.dataframe(table.round(2), hide_index=True)
    st.write(f"Total fixed expenses per month: **{an.format_inr(recurring['monthly_amount'].sum())}**")

    # Delete option
    st.write("Delete a recurring expense:")
    delete_id = st.selectbox("Select ID", list(recurring["id"]), key="delete_recurring_id")
    if st.button("Delete"):
        db.delete_recurring_expense(user_id, int(delete_id))
        st.rerun()          # reload the page so the table is updated


# ---------------------------------------------------------------------
# Currency converter (REST API)
# ---------------------------------------------------------------------
def show_currency():
    st.subheader("Currency Converter")
    col1, col2 = st.columns(2)
    from_currency = col1.selectbox("From currency", api.CURRENCIES)
    amount = col2.number_input("Amount", min_value=0.0, value=10.0, step=1.0)

    if st.button("Convert to INR"):
        if amount <= 0:
            st.error("Amount must be greater than 0.")
            return
        with st.spinner("Getting exchange rate..."):
            rate, converted, error = api.convert_to_inr(amount, from_currency)
        if error:
            st.error(error)
        else:
            st.write(f"Exchange Rate: 1 {from_currency} = {rate:.4f} INR")
            st.write(f"Approximate INR: {an.format_inr(converted)}")
