"""Expense History page: table, filters (Feature 1) and CSV export (Feature 6)."""

from datetime import date

import streamlit as st

import analysis as an
import auth
import database as db


def show():
    user_id = auth.get_user_id()
    st.title("Expense History")

    first_date, last_date = db.get_date_range(user_id)
    if first_date is None:
        st.info("No expenses found. Add some expenses first.")
        return

    default_start = first_date
    default_end = max(last_date, date.today())

    # When this page is opened, put the filter boxes at their default values
    if "h_start" not in st.session_state:
        st.session_state["h_start"] = default_start
        st.session_state["h_end"] = default_end
        st.session_state["h_category"] = "All"
        st.session_state["h_payment"] = "All"
        st.session_state["filters"] = None      # None = show all expenses

    def reset_filters():
        st.session_state["h_start"] = default_start
        st.session_state["h_end"] = default_end
        st.session_state["h_category"] = "All"
        st.session_state["h_payment"] = "All"
        st.session_state["filters"] = None

    # ---- Filter form ----
    st.subheader("Filters")
    col1, col2, col3, col4 = st.columns(4)
    start_date = col1.date_input("Start date", key="h_start", min_value=date(2000, 1, 1))
    end_date = col2.date_input("End date", key="h_end", min_value=date(2000, 1, 1))
    category = col3.selectbox("Category", ["All"] + db.CATEGORIES, key="h_category")
    payment = col4.selectbox("Payment method", ["All"] + db.PAYMENT_METHODS, key="h_payment")

    btn1, btn2, _ = st.columns([1, 1, 6])
    if btn1.button("Apply Filter"):
        if start_date > end_date:
            st.error("Start date cannot be after the end date.")
        else:
            st.session_state["filters"] = {
                "start_date": start_date,
                "end_date": end_date,
                "category": None if category == "All" else category,
                "payment_method": None if payment == "All" else payment,
            }
    btn2.button("Reset Filter", on_click=reset_filters)

    # ---- Get the data (SQL WHERE / BETWEEN) ----
    filters = st.session_state.get("filters") or {}
    df = db.get_expenses(user_id, **filters)

    if df.empty:
        st.warning("No expenses found for the selected filters.")
        return

    stats = db.get_filtered_stats(user_id, **filters)

    st.subheader("Result")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Expense", an.format_inr(stats["total"]))
    c2.metric("Transactions", stats["count"])
    c3.metric("Average Expense", an.format_inr(stats["average"]))
    c4.metric("Highest Expense", an.format_inr(stats["highest"]))

    table = df.rename(columns=an.DISPLAY_COLUMNS)
    st.dataframe(table, hide_index=True)

    # ---- CSV export (uses the same filtered data) ----
    csv_data = table.to_csv(index=False).encode("utf-8")
    st.download_button("Download Expense Report", data=csv_data,
                       file_name="expense_report.csv", mime="text/csv")
