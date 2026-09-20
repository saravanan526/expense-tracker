from datetime import date

import streamlit as st

import analysis as an
import auth
import database as db


def show():
    user_id = auth.get_user_id()
    

    st.title("Expense Tracker and Data Analytics Dashboard")
    st.write(f"Welcome, {auth.get_user()['full_name']}")

    overall = db.get_filtered_stats(user_id)   # no filters = all expenses
    if overall["count"] == 0:
        st.info("No expenses found. Go to 'Add Expense' to add one, "
                "or load the sample data from that page.")
        return

    today = date.today()
    this_month = db.get_month_stats(user_id, today.year, today.month)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Expense", an.format_inr(overall["total"]))
    col2.metric("This Month", an.format_inr(this_month["total"]))
    col3.metric("Transactions", overall["count"])
    col4.metric("Average Expense", an.format_inr(overall["average"]))

    # ---- Spending summary for the current month ----
    st.subheader("Spending Summary (This Month)")

    month_df = db.get_month_expenses(user_id, today.year, today.month)
    prev_year, prev_month = an.previous_month(today.year, today.month)
    previous = db.get_month_stats(user_id, prev_year, prev_month)
    comparison = an.compare_months(this_month["total"], previous["total"], previous["count"])

    for line in an.generate_summary(month_df, comparison):
        st.write("- " + line)

    # ---- Recent expenses ----
    st.subheader("Recent Expenses")
    recent = db.get_recent_expenses(user_id, 5)
    st.dataframe(recent.rename(columns=an.DISPLAY_COLUMNS), hide_index=True)
