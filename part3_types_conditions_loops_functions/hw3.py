#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"
INCOME = "income"
COST = "cost"
STATS = "stats"

number_of_date_parts = 3
number_of_month = 12
days_in_other_montth = [30, 31]
days_in_februaty = [28, 29]
income_querry_parts = 3
cost_querry_parts = 4
categories_querry_parts = 4
stats_querry_parts = 2

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": (),
}

financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    if year % 4 != 0:
        return False
    if year % 100 != 0:
        return True
    return year % 400 == 0


def days_in_month(month: int, year: int) -> int:
    if month in (1, 3, 5, 7, 8, 10, 12):
        return days_in_other_montth[1]
    if month in (4, 6, 9, 11):
        return days_in_other_montth[0]
    if is_leap_year(year):
        return days_in_februaty[1]
    return days_in_februaty[0]


def extract_date(date: str) -> tuple[int, int, int] | None:
    parts = date.split("-")
    if len(parts) != number_of_date_parts:
        return None

    day_str, month_str, year_str = parts
    if not (day_str.isdigit() and month_str.isdigit() and year_str.isdigit()):
        return None

    day = int(day_str)
    month = int(month_str)
    year = int(year_str)

    if year <= 0:
        return None
    if not (1 <= month <= number_of_month):
        return None

    dim = days_in_month(month, year)
    if day < 1 or day > dim:
        return None

    return day, month, year


def category_exists(category_name: str) -> bool:
    if "::" not in category_name:
        return False
    common, target = category_name.split("::", 1)
    if common not in EXPENSE_CATEGORIES:
        return False
    return target in EXPENSE_CATEGORIES[common]


def cost_categories_handler() -> str:
    return "\n".join(
        f"{k}::{v}"
        for k, kv in EXPENSE_CATEGORIES.items()
        for v in kv
    )


def date_loweq(d1: tuple[int, int, int], d2: tuple[int, int, int]) -> bool:
    y1, y2 = d1[2], d2[2]
    if y1 != y2:
        return y1 < y2
    m1, m2 = d1[1], d2[1]
    if m1 != m2:
        return m1 < m2
    return d1[0] <= d2[0]


def one_month(d1: tuple[int, int, int], d2: tuple[int, int, int]) -> bool:
    return d1[1] == d2[1] and d1[2] == d2[2]


def aggregate_stats(report_tuple: tuple[int, int, int]) -> tuple[float, float, float, dict[str, float]]:
    total_capital = 0.0
    month_income = 0.0
    month_expenses = 0.0
    expenses_by_categories: dict[str, float] = {}

    for item in financial_transactions_storage:
        item_date = item["date"]
        if not date_loweq(item_date, report_tuple):
            continue
        if item["type"] == INCOME:
            total_capital += item["amount"]
            if one_month(item_date, report_tuple):
                month_income += item["amount"]
        elif item["type"] == COST:
            total_capital -= item["amount"]
            if one_month(item_date, report_tuple):
                month_expenses += item["amount"]
                categories = item["category"]
                expenses_by_categories[categories] = expenses_by_categories.get(categories, 0.0) + item["amount"]

    return total_capital, month_income, month_expenses, expenses_by_categories


def profit_or_loss(month_income: float, month_expenses: float) -> str:
    diff = month_income - month_expenses
    if diff >= 0:
        return f"This month, the profit amounted to {diff:.2f} rubles."
    return f"This month, the loss amounted to {abs(diff):.2f} rubles."


def format_stats(expenses_by_categorie: dict[str, float]) -> list[str]:
    lines: list[str] = []
    lines.append("Details (category: amount):")
    if expenses_by_categorie:
        sorted_items = sorted(expenses_by_categorie.items(), key=lambda x: x[0])
        for idx, (cat, amount) in enumerate(sorted_items, start=1):
            lines.append(f"{idx}. {cat}: {amount:.2f}")
    return lines


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    parsed_date = extract_date(income_date)
    if parsed_date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append(
        {
            "type": INCOME,
            "amount": amount,
            "date": parsed_date,
        }
    )
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    parsed_date = extract_date(income_date)
    if parsed_date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    if not category_exists(category_name):
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY

    financial_transactions_storage.append(
        {
            "type": COST,
            "category": category_name,
            "amount": amount,
            "date": parsed_date,
        }
    )
    return OP_SUCCESS_MSG


def stats_handler(report_date: str) -> str:
    report_d = extract_date(report_date)
    if report_d is None:
        return INCORRECT_DATE_MSG

    total_capital, month_income, month_expenses, expenses_by_categories = aggregate_stats(report_d)
    profit_loss_line = profit_or_loss(month_income, month_expenses)

    lines: list[str] = []
    lines.append(f"Your statistics as of {report_date}:")
    lines.append(f"Total capital: {total_capital:.2f} rubles")
    lines.append(profit_loss_line)
    lines.append(f"Income: {month_income:.2f} rubles")
    lines.append(f"Expenses: {month_expenses:.2f} rubles")
    lines.append("")
    lines.extend(format_stats(expenses_by_categories))
    return "\n".join(lines)


def handle_income_command(parts: list[str]) -> str:
    if len(parts) != income_querry_parts:
        return UNKNOWN_COMMAND_MSG

    amount_str = parts[1]
    date_str = parts[2]

    amount = float(amount_str)
    return income_handler(amount, date_str)


def handle_cost_add_command(parts: list[str]) -> str:
    if len(parts) != cost_querry_parts:
        return UNKNOWN_COMMAND_MSG

    category_name = parts[1]
    amount_str = parts[2]
    date_str = parts[3]

    amount = float(amount_str)
    result = cost_handler(category_name, amount, date_str)
    if result == NOT_EXISTS_CATEGORY:
        return NOT_EXISTS_CATEGORY + "\n" + cost_categories_handler()
    return result


def handle_stats_command(parts: list[str]) -> str:
    if len(parts) != stats_querry_parts:
        return UNKNOWN_COMMAND_MSG
    date_str = parts[1]
    return stats_handler(date_str)


def process_command(line: str) -> str:
    if not line:
        return ""

    parts = line.split()
    command = parts[0]

    if command == INCOME:
        return handle_income_command(parts)

    if command == COST and len(parts) == categories_querry_parts and parts[1] == "categories":
        return cost_categories_handler()

    if command == COST:
        return handle_cost_add_command(parts)

    if command == STATS:
        return handle_stats_command(parts)

    return UNKNOWN_COMMAND_MSG


def main() -> None:
    while True:
        line = input().strip()
        result = process_command(line)
        if result:
            print(result)


if __name__ == "__main__":
    main()
