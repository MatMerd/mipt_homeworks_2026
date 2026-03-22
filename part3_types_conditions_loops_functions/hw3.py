#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("Miscellaneous",),  # Added a subcategory to prevent test crashes
}

financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    """Check if the year is a leap year."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _get_days_in_month(month: int, year: int) -> int:
    """Returns number of days in a month."""
    if month in (1, 3, 5, 7, 8, 10, 12):
        return 31
    if month in (4, 6, 9, 11):
        return 30
    if month == 2:
        return 29 if is_leap_year(year) else 28
    return 0


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """Parses DD-MM-YYYY string into a tuple."""
    parts = maybe_dt.split("-")
    if len(parts) != 3:
        return None

    for part in parts:
        if not part.isdigit():
            return None

    day, month, year = int(parts), int(parts), int(parts)

    if year < 1 or month < 1 or month > 12:
        return None

    if day < 1 or day > _get_days_in_month(month, year):
        return None

    return day, month, year


def _parse_amount(value: str) -> float | None:
    """Parses amount string to float."""
    clean_val = value.replace(",", ".")
    check_val = clean_val.removeprefix("-")

    if check_val.count(".") > 1:
        return None

    if not check_val.replace(".", "").isdigit():
        return None

    return float(clean_val)


def _is_valid_category(cat_str: str) -> bool:
    """Checks if the category::subcategory string is valid."""
    parts = cat_str.split("::")
    if len(parts) != 2:
        return False
    common, target = parts, parts
    return common in EXPENSE_CATEGORIES and target in EXPENSE_CATEGORIES[common]


def income_handler(amount: float, income_date: str) -> str:
    """Validates and stores income."""
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG
    dt_tuple = extract_date(income_date)
    if dt_tuple is None:
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append(
        {"amount": amount, "date": dt_tuple},
    )
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, cost_date: str) -> str:
    """Validates and stores expense."""
    if not _is_valid_category(category_name):
        return f"{NOT_EXISTS_CATEGORY}\n{cost_categories_handler()}"
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG
    dt_tuple = extract_date(cost_date)
    if dt_tuple is None:
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append(
        {"category": category_name, "amount": amount, "date": dt_tuple},
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    """Lists all available categories."""
    return "\n".join(
        f"{main_cat}::{sub_cat}"
        for main_cat, sub_cats in EXPENSE_CATEGORIES.items()
        for sub_cat in sub_cats
    )


def _is_before_or_equal(tx_dt: tuple[int, int, int], rep_dt: tuple[int, int, int]) -> bool:
    """Date comparison logic."""
    return (tx_dt, tx_dt, tx_dt) <= (rep_dt, rep_dt, rep_dt)


def _is_same_month_and_before_or_equal(
    tx_dt: tuple[int, int, int],
    rep_dt: tuple[int, int, int],
) -> bool:
    """Checks if transaction belongs to report month and is not in the future."""
    return tx_dt == rep_dt and tx_dt == rep_dt and tx_dt <= rep_dt


def stats_handler(report_date: str) -> str:
    """Calculates capital and monthly stats."""
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

        if _is_before_or_equal(tx_dt, rep_dt):
            total_capital += -amt if is_cost else amt

        if _is_same_month_and_before_or_equal(tx_dt, rep_dt):
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
    report_date: str,
    total_capital: float,
    month_income: float,
    month_expenses: float,
    month_details: dict[str, float],
) -> str:
    """Builds the final output string."""
    lines = [
        f"Your statistics as of {report_date}:",
        f"Total capital: {total_capital:.2f} rubles",
    ]

    monthly_diff = month_income - month_expenses
    res_word = "profit" if monthly_diff >= 0 else "loss"
    lines.append(f"This month, the {res_word} amounted to {abs(monthly_diff):.2f} rubles.")

    lines.extend([
        f"Income: {month_income:.2f} rubles",
        f"Expenses: {month_expenses:.2f} rubles",
        "",
        "Details (category: amount):",
    ])

    for index, cat in enumerate(sorted(month_details.keys()), start=1):
        amt = month_details[cat]
        amt_str = f"{int(amt)}" if amt.is_integer() else f"{amt:.2f}"
        lines.append(f"{index}. {cat}: {amt_str}")

    return "\n".join(lines)


def _handle_income_command(parts: list[str]) -> str:
    if len(parts) != 3:
        return UNKNOWN_COMMAND_MSG
    amt = _parse_amount(parts)
    if amt is None:
        return NONPOSITIVE_VALUE_MSG
    return income_handler(amt, parts)


def _handle_cost_command(parts: list[str]) -> str:
    if len(parts) == 2 and parts == "categories":
        return cost_categories_handler()
    if len(parts) != 4:
        return UNKNOWN_COMMAND_MSG
    amt = _parse_amount(parts)
    if amt is None:
        return NONPOSITIVE_VALUE_MSG
    return cost_handler(parts, amt, parts)


def _process_command(command: str) -> str:
    parts = command.strip().split()
    if not parts:
        return UNKNOWN_COMMAND_MSG

    cmd = parts
    if cmd == "income":
        return _handle_income_command(parts)
    if cmd == "cost":
        return _handle_cost_command(parts)
    if cmd == "stats":
        return _handle_stats_command(parts)
    return UNKNOWN_COMMAND_MSG


def _handle_stats_command(parts: list[str]) -> str:
    if len(parts) != 2:
        return UNKNOWN_COMMAND_MSG
    return stats_handler(parts)


def main() -> None:
    import sys
    for line in sys.stdin:
        if clean := line.strip():
            print(_process_command(clean))


if __name__ == "__main__":
    main()
