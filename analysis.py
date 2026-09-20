"""
analysis.py
-----------
Data analysis with Pandas + charts with Matplotlib.
No Streamlit code here, only calculations and figures.
"""

import calendar

import matplotlib.pyplot as plt
import pandas as pd

# Colors used in all charts (same colors everywhere = consistent look)
BLUE = "#2E86AB"
ORANGE = "#F18F01"
GRAY = "#B0BEC5"
PALETTE = ["#2E86AB", "#F18F01", "#3BB273", "#E4572E", "#7768AE", "#17BEBB", "#FFC914"]

# Column names shown to the user (tables and CSV file)
DISPLAY_COLUMNS = {
    "id": "ID",
    "expense_date": "Date",
    "category": "Category",
    "amount": "Amount",
    "payment_method": "Payment Method",
    "description": "Description",
}


# ---------------------------------------------------------------------
# Small helper functions
# ---------------------------------------------------------------------
def format_inr(amount):
    """Format a number in Indian style. Example: 1234567.5 -> ₹12,34,567.50"""
    amount = round(float(amount), 2)
    sign = "-" if amount < 0 else ""
    whole, decimal = f"{abs(amount):.2f}".split(".")

    if len(whole) > 3:
        last_three = whole[-3:]
        rest = whole[:-3]
        parts = []
        while len(rest) > 2:
            parts.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            parts.insert(0, rest)
        whole = ",".join(parts) + "," + last_three

    return f"{sign}₹{whole}.{decimal}"


def month_label(year, month):
    """Example: (2026, 9) -> 'Sep 2026'"""
    return f"{calendar.month_abbr[int(month)]} {int(year)}"


def previous_month(year, month):
    """Return (year, month) of the month before the given month."""
    if month == 1:
        return year - 1, 12
    return year, month - 1


# ---------------------------------------------------------------------
# Data cleaning
# ---------------------------------------------------------------------
def clean_data(df):
    """Basic cleaning: correct data types, remove bad rows, fill empty text."""
    if df.empty:
        return df.copy()

    df = df.copy()
    df["expense_date"] = pd.to_datetime(df["expense_date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["expense_date", "amount"])
    df["description"] = df["description"].fillna("")
    return df


def add_percentage(df, value_column="total"):
    """Add a 'percentage' column (share of each row in the total)."""
    df = df.copy()
    grand_total = df[value_column].sum()
    if grand_total > 0:
        df["percentage"] = (df[value_column] / grand_total * 100).round(2)
    else:
        df["percentage"] = 0.0
    return df


def add_month_label(monthly_df):
    """Add a 'month' text column like 'Aug 2026' to the monthly totals table."""
    df = monthly_df.copy()
    df["label"] = [month_label(y, m) for y, m in zip(df["year"], df["month"])]
    return df


# ---------------------------------------------------------------------
# Budget analysis
# ---------------------------------------------------------------------
def calculate_budget_status(budget, spent):
    """
    Remaining   = Budget - Spent
    Utilization = (Spent / Budget) x 100

    below 80%   -> Normal spending
    80% - 100%  -> Budget nearing limit
    above 100%  -> Budget exceeded

    Returns None when the budget is missing or zero (cannot divide by zero).
    """
    if budget is None or budget <= 0:
        return None

    remaining = budget - spent
    utilization = (spent / budget) * 100

    if utilization < 80:
        status = "Normal spending"
        level = "ok"
    elif utilization <= 100:
        status = "Budget nearing limit"
        level = "warning"
    else:
        status = "Budget exceeded"
        level = "error"

    return {
        "budget": budget,
        "spent": spent,
        "remaining": remaining,
        "utilization": utilization,
        "status": status,
        "level": level,
    }


# ---------------------------------------------------------------------
# Monthly comparison
# ---------------------------------------------------------------------
def compare_months(current_total, previous_total, previous_count):
    """
    Difference         = Current Month - Previous Month
    Percentage Change  = (Difference / Previous Month) x 100
    """
    difference = current_total - previous_total

    # No previous month data or previous month = 0 -> cannot calculate percentage
    if previous_count == 0:
        return {
            "current": current_total,
            "previous": previous_total,
            "difference": difference,
            "percent": None,
            "message": "No expense data found for the previous month, so the change cannot be calculated.",
        }
    if previous_total == 0:
        return {
            "current": current_total,
            "previous": previous_total,
            "difference": difference,
            "percent": None,
            "message": "Previous month expense is zero, so the percentage change cannot be calculated.",
        }

    percent = (difference / previous_total) * 100

    if difference > 0:
        message = f"Spending increased by {abs(percent):.1f}% compared to the previous month."
    elif difference < 0:
        message = f"Spending decreased by {abs(percent):.1f}% compared to the previous month."
    else:
        message = "Spending is the same as the previous month."

    return {
        "current": current_total,
        "previous": previous_total,
        "difference": difference,
        "percent": percent,
        "message": message,
    }


# ---------------------------------------------------------------------
# Fixed vs variable expenses
# ---------------------------------------------------------------------
def monthly_equivalent(amount, frequency):
    """Convert a recurring amount to its monthly amount."""
    frequency = str(frequency).lower()
    if frequency == "weekly":
        return amount * 52 / 12
    if frequency == "yearly":
        return amount / 12
    return amount  # monthly


def add_monthly_amount(recurring_df):
    """Add a 'monthly_amount' column to the recurring expenses table."""
    df = recurring_df.copy()
    df["monthly_amount"] = [
        monthly_equivalent(a, f) for a, f in zip(df["amount"], df["frequency"])
    ]
    return df


def fixed_vs_variable(fixed_total, variable_total):
    """Fixed = recurring expenses, Variable = normal daily expenses."""
    total = fixed_total + variable_total
    if total > 0:
        fixed_pct = fixed_total / total * 100
        variable_pct = variable_total / total * 100
    else:
        fixed_pct = 0.0
        variable_pct = 0.0

    return {
        "fixed": fixed_total,
        "variable": variable_total,
        "total": total,
        "fixed_pct": fixed_pct,
        "variable_pct": variable_pct,
    }


# ---------------------------------------------------------------------
# Rule-based spending summary (plain Python, no AI)
# ---------------------------------------------------------------------
def generate_summary(df, comparison=None, period="this month"):
    """Return a list of sentences describing the spending in df."""
    df = clean_data(df)
    if df.empty:
        return [f"No expenses recorded {period}."]

    total = df["amount"].sum()
    by_category = df.groupby("category")["amount"].sum()

    top_category = by_category.idxmax()
    top_amount = by_category.max()
    low_category = by_category.idxmin()
    low_amount = by_category.min()
    top_percent = top_amount / total * 100

    biggest = df.loc[df["amount"].idxmax()]
    biggest_date = biggest["expense_date"].strftime("%d %b %Y")

    lines = [
        f"{top_category} is your highest spending category {period}.",
        f"You spent {format_inr(top_amount)} on {top_category}.",
        f"{top_category} represents {top_percent:.0f}% of total expenses.",
        f"Lowest spending category: {low_category} ({format_inr(low_amount)}).",
        f"Highest single expense: {format_inr(biggest['amount'])} on {biggest_date} ({biggest['category']}).",
        f"Average transaction: {format_inr(df['amount'].mean())}.",
        f"Number of transactions: {len(df)}.",
    ]

    if comparison is not None:
        lines.append(f"Monthly comparison: {comparison['message']}")

    return lines


# ---------------------------------------------------------------------
# Matplotlib charts (each function returns a figure)
# ---------------------------------------------------------------------
def bar_chart(labels, values, title, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(7, 4))
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(labels))]
    ax.bar(labels, values, color=colors)
    ax.set_title(title, color="#1F2933")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", alpha=0.3)
    ax.set_axisbelow(True)
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    fig.tight_layout()
    return fig


def line_chart(labels, values, title, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(labels, values, marker="o", color=BLUE, linewidth=2)
    ax.fill_between(range(len(values)), values, color=BLUE, alpha=0.12)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    return fig


def comparison_chart(previous_label, previous_total, current_label, current_total):
    fig, ax = plt.subplots(figsize=(5, 4))
    bars = ax.bar([previous_label, current_label], [previous_total, current_total],
                  color=[GRAY, BLUE])
    ax.set_title("Previous Month vs Current Month")
    ax.set_ylabel("Total Expense (Rs)")
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f"{bar.get_height():,.0f}", ha="center", va="bottom")
    fig.tight_layout()
    return fig


def fixed_variable_chart(fixed_total, variable_total):
    fig, ax = plt.subplots(figsize=(5, 4))
    bars = ax.bar(["Fixed", "Variable"], [fixed_total, variable_total],
                  color=[ORANGE, BLUE])
    ax.set_title("Fixed vs Variable Expenses")
    ax.set_ylabel("Amount (Rs)")
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f"{bar.get_height():,.0f}", ha="center", va="bottom")
    fig.tight_layout()
    return fig
