#!/usr/bin/env python

import sys
from typing import Any

# Error messages
UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

# Constants for magic values
DATE_PARTS_COUNT = 3
MONTHS_IN_YEAR = 12
FEBRUARY = 2
CATEGORY_PARTS_COUNT = 2
INCOME_ARGS_COUNT = 3
COST_ARGS_COUNT = 4
STATS_ARGS_COUNT = 2
CATEGORIES_LIST_CMD_LEN = 2

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("Miscellaneous",),
}

financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    """Check if the year is a leap year."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _get_days_in_month(month: int, year: int) -> int:
    """Return the number of days in a given month."""
    if month in (1, 3, 5, 7, 8, 10, 12):
        return 31
    if month in (4, 6, 9, 11):
        return 30
    if month == FEBRUARY:
        return 29 if is_leap_year(year) else 28
    return 0


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """Parse DD-MM-YYYY string into a tuple (day, month, year)."""
    parts = maybe_dt.split("-")
    if len(parts) != DATE_PARTS_COUNT:
        return None

    for part in parts:
        if not part.isdigit():
            return None

    day, month, year = int(parts), int(parts), int(parts)

    if year < 1 or month < 1 or month > MONTHS_IN_YEAR:
        return None

    if day < 1 or day > _get_days_in_month(month, year):
        return None

    return day, month, year


def _parse_amount(value: str) -> float | None:
    """Safely parse amount from string."""
    clean_val = value.replace(",", ".")
    check_val = clean_val.removeprefix("-")

    if check_val.count(".") > 1:
        return None

    if not check_val.replace(".", "").isdigit():
        return None

    return float(clean_val)


def _is_valid_category(cat_str: str) -> bool:
    """Check if the category string is valid."""
    parts = cat_str.split("::")
    if len(parts) != CATEGORY_PARTS_COUNT:
        return False
    common, target = parts, parts
    return common in EXPENSE_CATEGORIES and target in EXPENSE_CATEGORIES[common]


def income_handler(amount: float, income_date: str) -> str:
    """Handle income addition."""
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG
    dt_tuple = extract_date(income_date)
    if dt_tuple is None:
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({"amount": amount, "date": dt_tuple})
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, cost_date: str) -> str:
    """Handle expense addition."""
    if not _is_valid_category(category_name):
        return f"{NOT_EXISTS_CATEGORY}\n{cost_categories_handler()}"
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG
    dt_tuple = extract_date(cost_date)
    if dt_tuple is None:
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({
        "category": category_name,
        "amount": amount,
        "date": dt_tuple,
    })
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    """Return all available expense categories."""
    return "\n".join(
        f"{m}::{s}" for m, subs in EXPENSE_CATEGORIES.items() for s in subs
    )


def stats_handler(report_date: str) -> str:
    """Calculate and format financial statistics."""
    rep_dt = extract_date(report_date)
    if not rep_dt:
        return INCORRECT_DATE_MSG

    total_capital = 0.0
    month_income = 0.0
    month_expenses = 0.0
    month_details: dict[str, float] = {}

    for tx in financial_transactions_storage:
        tx_dt = tx["date"]
        amt = tx["amount"]
        is_cost = "category" in tx

        tx_comp = (tx_dt, tx_dt, tx_dt)
        rep_comp = (rep_dt, rep_dt, rep_dt)

        if tx_comp <= rep_comp:
            total_capital += -amt if is_cost else amt

        if tx_dt == rep_dt and tx_dt == rep_dt and tx_dt <= rep_dt:
            if is_cost:
                month_expenses += amt
                cat = str(tx["category"])
                month_details[cat] = month_details.get(cat, 0.0) + amt
            else:
                month_income += amt

    return _format_stats_output(
        report_date, total_capital, month_income, month_expenses, month_details
    )


def _format_stats_output(
    date_str: str,
    capital: float,
    income: float,
    expenses: float,
    details: dict[str, float],
) -> str:
    """Format final output string."""
    diff = income - expenses
    res_type = "profit" if diff >= 0 else "loss"
    lines = [
        f"Your statistics as of {date_str}:",
        f"Total capital: {capital:.2f} rubles",
        f"This month, the {res_type} amounted to {abs(diff):.2f} rubles.",
        f"Income: {income:.2f} rubles",
        f"Expenses: {expenses:.2f} rubles",
        "",
        "Details (category: amount):",
    ]
    for i, cat in enumerate(sorted(details.keys()), 1):
        amt = details[cat]
        amt_f = f"{int(amt)}" if amt.is_integer() else f"{amt:.2f}"
        lines.append(f"{i}. {cat}: {amt_f}")
    return "\n".join(lines)


def _process_command(command: str) -> str:
    """Main command router."""
    parts = command.strip().split()
    if not parts:
        return UNKNOWN_COMMAND_MSG

    cmd = parts
    if cmd == "income" and len(parts) == INCOME_ARGS_COUNT:
        amt = _parse_amount(parts)
        return income_handler(amt, parts) if amt is not None else NONPOSITIVE_VALUE_MSG

    if cmd == "cost":
        if len(parts) == CATEGORIES_LIST_CMD_LEN and parts == "categories":
            return cost_categories_handler()
        if len(parts) == COST_ARGS_COUNT:
            amt = _parse_amount(parts)
            return cost_handler(parts, amt, parts) if amt is not None else NONPOSITIVE_VALUE_MSG

    if cmd == "stats" and len(parts) == STATS_ARGS_COUNT:
        return stats_handler(parts)

    return UNKNOWN_COMMAND_MSG


def main() -> None:
    """Entry point."""
    for line in sys.stdin:
        if clean := line.strip():
            print(_process_command(clean))


if __name__ == "__main__":
    main()
