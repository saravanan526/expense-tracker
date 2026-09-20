"""Analytics page: Matplotlib charts, plus Fixed vs Variable analysis (Feature 5)."""

import matplotlib.pyplot as plt
import streamlit as st

import analysis as an
import auth
import database as db


def show_chart(fig):
    st.pyplot(fig)
    plt.close(fig)


def show():
    user_id = auth.get_user_id()
    st.title("Analytics")

    monthly = db.get_monthly_totals(user_id)
    if monthly.empty:
        st.info("No expenses found. Add some expenses to see the analytics.")
        return

    monthly = an.add_month_label(monthly)

    # ---- Month selection (used by category, payment and daily charts) ----
    options = ["All Months"] + list(monthly["label"])
    selected = st.selectbox("Select period", options)

    if selected == "All Months":
        year, month = None, None
    else:
        row = monthly[monthly["label"] == selected].iloc[0]
        year, month = int(row["year"]), int(row["month"])

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Category-wise", "Monthly", "Payment Method", "Daily Trend", "Fixed vs Variable"]
    )

    # ---- 1. Category-wise bar chart ----
    with tab1:
        category_df = an.add_percentage(db.get_category_totals(user_id, year, month))
        if category_df.empty:
            st.warning("No data available.")
        else:
            fig = an.bar_chart(category_df["category"], category_df["total"],
                               "Category-wise Expenses", "Category", "Total Expense (Rs)")
            show_chart(fig)
            st.dataframe(category_df.rename(columns={
                "category": "Category", "total": "Total", "percentage": "Percentage (%)"}),
                hide_index=True)

    # ---- 2. Monthly line chart (always all months) ----
    with tab2:
        fig = an.line_chart(monthly["label"], monthly["total"],
                            "Monthly Expenses", "Month", "Total Expense (Rs)")
        show_chart(fig)
        st.dataframe(monthly[["label", "total"]].rename(columns={
            "label": "Month", "total": "Total"}), hide_index=True)

    # ---- 3. Payment method bar chart ----
    with tab3:
        payment_df = an.add_percentage(db.get_payment_totals(user_id, year, month))
        if payment_df.empty:
            st.warning("No data available.")
        else:
            fig = an.bar_chart(payment_df["payment_method"], payment_df["total"],
                               "Payment Method Analysis", "Payment Method", "Total Expense (Rs)")
            show_chart(fig)
            st.dataframe(payment_df.rename(columns={
                "payment_method": "Payment Method", "total": "Total",
                "percentage": "Percentage (%)"}), hide_index=True)

    # ---- 4. Daily trend line chart ----
    with tab4:
        daily_df = db.get_daily_totals(user_id, year, month)
        if daily_df.empty:
            st.warning("No data available.")
        else:
            dates = [d.strftime("%d %b") for d in daily_df["expense_date"]]
            fig = an.line_chart(dates, daily_df["total"],
                                "Daily Expense Trend", "Date", "Total Expense (Rs)")
            show_chart(fig)

    # ---- 5. Fixed vs Variable ----
    with tab5:
        show_fixed_vs_variable(user_id, monthly, year, month)


def show_fixed_vs_variable(user_id, monthly, year, month):
    st.write("Fixed expenses = recurring expenses (converted to a monthly amount). "
             "Variable expenses = normal daily expenses of the month.")

    # This analysis needs one month. If "All Months" is selected, use the latest month.
    if year is None:
        last_row = monthly.iloc[-1]
        year, month = int(last_row["year"]), int(last_row["month"])
    st.write(f"Month: **{an.month_label(year, month)}**")

    recurring = db.get_recurring_expenses(user_id)
    if recurring.empty:
        st.warning("No recurring expenses added yet. Add them in Budget Analysis > Recurring Expenses.")
        fixed_total = 0.0
    else:
        recurring = an.add_monthly_amount(recurring)
        fixed_total = float(recurring["monthly_amount"].sum())

    variable_total = db.get_month_stats(user_id, year, month)["total"]
    result = an.fixed_vs_variable(fixed_total, variable_total)

    c1, c2, c3 = st.columns(3)
    c1.metric("Fixed Expenses", an.format_inr(result["fixed"]))
    c2.metric("Variable Expenses", an.format_inr(result["variable"]))
    c3.metric("Total Expenses", an.format_inr(result["total"]))

    if result["total"] == 0:
        st.warning("No fixed or variable expenses found, so percentages cannot be calculated.")
        return

    st.write(f"Fixed: {result['fixed_pct']:.1f}%  |  Variable: {result['variable_pct']:.1f}%")
    show_chart(an.fixed_variable_chart(result["fixed"], result["variable"]))
