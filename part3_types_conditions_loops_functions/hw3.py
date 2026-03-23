#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"
NOT_EXISTS_CATEGORY = "Category not exists!"

INCOME_COMMAND = "income"
COST_COMMAND = "cost"
STATS_COMMAND = "stats"
KEY_DATE = "date"
KEY_TYPE = "type"
KEY_AMOUNT = "amount"
KEY_CATEGORY = "categories"

INCOME_COMMAND_PARTS = 3
COST_COMMAND_PARTS = 4
STATS_COMMAND_PARTS = 2

DATE_PARTS_COUNT = 3
CATEGORY_NAME_PARTS_COUNT = 2
MONTHS_IN_YEAR = 12
CATEGORIES_PARTS = 4
DAYS_IN_LONG_MONTHS = 31
DAYS_IN_SMALL_MONTHS = 30
FEBRUARY = 2
SMALL_MONTHS = {4, 6, 9, 11}
LONG_MONTHS = {1, 3, 5, 7, 8, 10, 12}
DateTuple = tuple[int, int, int]

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("SomeCategory", "SomeOtherCategory"),
}

financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 400 == 0


def days_in_month(month: int, year: int) -> int:
    if month == FEBRUARY and is_leap_year(year):
        return 29
    if month == FEBRUARY and not is_leap_year(year):
        return 28
    if month in SMALL_MONTHS:
        return DAYS_IN_SMALL_MONTHS
    return DAYS_IN_LONG_MONTHS


def is_valid_day_and_month(day: int, month: int, year: int) -> bool:
    return 1 <= month <= MONTHS_IN_YEAR and 1 <= day <= days_in_month(month, year)

def extract_date(maybe_date: str) -> tuple[int, int, int] | None:
    parts = maybe_date.split("-")
    if len(parts) != DATE_PARTS_COUNT:
        return None

    if not all(date_part.isdigit() for date_part in parts):
        return None

    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2])

    if not is_valid_day_and_month(day, month, year):
        return None

    if day <= days_in_month(month, year):
        return day, month, year
    return None


def income_handler(amount: float, date_str: str) -> str:

    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG
    date_value = extract_date(date_str)
    financial_transactions_storage.append({
        KEY_TYPE: INCOME_COMMAND,
        KEY_AMOUNT: amount,
        KEY_DATE: date_value,
    })
    return OP_SUCCESS_MSG


def is_category_valid(category_name: str) -> bool:
    parts = category_name.split("::")
    if len(parts) != CAT_PARTS_COUNT:
        return False
    common, target = parts
    return target in EXPENSE_CATEGORIES.get(common, ())


def cost_handler(category_name: str, amount: float, date_str: str) -> str:
    date_value = extract_date(date_str)

    if date_value is None or amount <= 0 or not is_category_valid(category_name):
        financial_transactions_storage.append({})
        if date_value is None:
            return INCORRECT_DATE_MSG
        if amount <= 0:
            return NONPOSITIVE_VALUE_MSG
        return NOT_EXISTS_CATEGORY

    financial_transactions_storage.append({
        KEY_TYPE: COST,
        KEY_CATEGORY: category_name,
        KEY_AMOUNT: amount,
        KEY_DATE: parsed_date,
    })
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    lines = []
    for category, subcategories in EXPENSE_CATEGORIES.items():
        for subcategory in subcategories:
            lines.append(f"{category}::{subcategory}")
    return "\n".join(lines)


def date_lower(date_one: DateTuple, date_other: DateTuple) -> bool:
    if date_one[2] != date_other[2]:
        return date_one[2] < date_other[2]
    if date_one[1] != date_other[1]:
        return date_one[1] < date_other[1]
    return date_one[0] <= date_other[0]

def same_month(date_one: DateTuple, date_other: DateTuple) -> bool:
    equal_months = date_one[1] == date_other[1]
    eaqual_year = date_one[2] == date_other[2]
    return equal_months and equal_year


def update_totals_for_income(
    item: dict[str, Any],
    report: DateTuple,
    total_capital: float,
    month_income: float,
) -> tuple[float, float]:
    item_date = item[KEY_DATE]
    if not one_month(item_date, report):
        return total_capital + item[KEY_AMOUNT], month_income
    total_capital += item[KEY_AMOUNT]
    month_income += item[KEY_AMOUNT]
    return total_capital, month_income


def update_totals_for_cost(
    item: dict[str, Any],
    report: DateTuple,
    total_capital: float,
    month_expenses: float,
    expenses_by_cat: dict[str, float],
) -> tuple[float, float, dict[str, float]]:
    item_date = item[KEY_DATE]
    amount = item[KEY_AMOUNT]
    total_capital -= amount    
    if same_month(item_date, report):
        month_expenses += amount
        category = item[KEY_CATEGORY]
        expenses_by_cat[category] = expenses_by_cat.get(category, 0) + amount    
    return total_capital, month_expenses, expenses_by_cat


def final_stats(
    report_tuple: DateTuple,
) -> tuple[float, float, float, dict[str, float]]:
    total_capital: float = 0
    month_income: float = 0
    month_expenses: float = 0
    expenses_by_category: dict[str, float] = {}

    for item in financial_transactions_storage:
        if not date_lower(item[KEY_DATE], report_tuple):
            continue

        if item[KEY_TYPE] == INCOME:
            total_capital, month_income = update_totals_for_income(
                item, report_tuple, total_capital, month_income,
            )
        elif item[KEY_TYPE] == COST:
            total_capital, month_expenses = update_totals_for_cost(
                item, report_tuple, total_capital, month_expenses, expenses_by_category,
            )

    return total_capital, month_income, month_expenses, expenses_by_category


def profit_loss (month_income: float, month_expenses: float) -> str:
    delta = month_income - month_expenses
    if delta >= 0:
        return f"This month, the profit amounted to {delta:.2f} rubles."
    return f"This month, the loss amounted to {abs(delta):.2f} rubles."


def format_stats(expenses_by_categories: dict[str, float]) -> list[str]:
    lines: list[str] = []
    lines.append("Details (category: amount):")
    if expenses_by_categories:
        sorted_items = sorted(expenses_by_categories.items(), key = lambda x: x[0])
        for index, (category, amount) in enumerate(sorted_items, start=1):
            lines.append(f"{index}. {category}: {amount:.2f}")
    return lines


def stats_handler(report_date: str) -> str:
    report_d = extract_date(report_date)
    if report_d is None:
        return INCORRECT_DATE_MSG
    stats = final_stats(report_d)

    lines: list[str] = []
    lines.append(f"Your statistics as of {report_date}:")
    lines.append(f"Total capital: {stats[0]:.2f} rubles")
    lines.append(profit_loss(stats[1], stats[2]))
    lines.append(f"Income: {stats[1]:.2f} rubles")
    lines.append(f"Expenses: {stats[2]:.2f} rubles")
    lines.append("")
    lines.extend(format_stats(stats[3]))
    return "\n".join(lines)
    
def handle_income_command(parts: list[str]) -> str:
    if len(parts) != INCOME_COMMAND_PARTS:
        return UNKNOWN_COMMAND_MSG
    return income_handler(float(parts[1]), parts[2])

def handle_cost_add_command(parts: list[str]) -> str:
    if len(parts) != COST_COMMAND_PARTS:
        return UNKNOWN_COMMAND_MSG
    result = cost_handler(parts[1], float(parts[2]), parts[3])
    if result == NOT_EXISTS_CATEGORY:
        return f"{NOT_EXISTS_CATEGORY}\n{cost_categories_handler()}"
    return result


def handle_stats_command(parts: list[str]) -> str:
    if len(parts) != STATS_COMMAND_PARTS:
        return UNKNOWN_COMMAND_MSG
    return stats_handler(parts[1])


def command_handler(command: str, parts: list[str]) -> str | None:
    if command == INCOME_COMMAND:
        return handle_income_command(parts)
    is_cost_command = command == COST_COMMAND
    has_categories_len = len(parts) == CATEGORIES_PARTS
    is_categories_subcommand = parts[1] == KEY_CATEGORY

    if is_cost_command and has_categories_len and is_categories_subcommand:
        return cost_categories_handler()

    if command == COST_COMMAND:
        return handle_cost_add_command(parts)

    if command == STATS_COMMAND:
        return handle_stats_command(parts)
    return None


def work_command(line: str) -> str | None:
    if not line:
        return None
    parts = line.split()
    result = command_handler(parts[0], parts[1])
    if result is not None:
        return result
    return UNKNOWN_COMMAND_MSG


def main() -> None:
    line = input().strip()
    while line:
        result = work_command(line)
        if result:
            print(result)
        line = input().strip()


if __name__ == "__main__":
    main()
