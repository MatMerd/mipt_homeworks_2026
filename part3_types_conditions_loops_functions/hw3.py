#!/usr/bin/env python

import re
from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

AMOUNT_KEY = "amount"
DATE_KEY = "date"
CATEGORY_KEY = "category"
ZERO_AMOUNT = float(0)

Date = tuple[int, int, int]

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

DATE_PARTS_COUNT = 3
DAY_LEN = 2
MONTH_LEN = 2
YEAR_LEN = 4
MIN_MONTH = 1
MAX_MONTH = 12
FEBRUARY = 2


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    if year % 100 == 0:
        return year % 400 == 0
    return year % 4 == 0


def get_days_in_month(month: int, year: int) -> int:
    if month == FEBRUARY:
        return 29 if is_leap_year(year) else 28
    if month in [4, 6, 9, 11]:
        return 30
    return 31


def extract_date(maybe_dt: str) -> Date | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    match = re.fullmatch(r"(\d{2})-(\d{2})-(\d{4})", maybe_dt)
    if match is None:
        return None

    day, month, year = map(int, match.groups())
    if day < MIN_MONTH or month < MIN_MONTH or month > MAX_MONTH:
        return None
    if day > get_days_in_month(month, year):
        return None
    return day, month, year


def is_valid_category(category_name: str) -> bool:
    parts = category_name.split("::")
    if len(parts) != 1 + 1:
        return False
    common_category, target_category = parts
    return common_category in EXPENSE_CATEGORIES and target_category in EXPENSE_CATEGORIES[common_category]


def date_to_comparable(date_value: Date) -> Date:
    day, month, year = date_value
    return year, month, day


def save_error(error_message: str) -> str:
    financial_transactions_storage.append({})
    return error_message


def save_income(amount: float, parsed_date: Date) -> str:
    financial_transactions_storage.append({AMOUNT_KEY: amount, DATE_KEY: parsed_date})
    return OP_SUCCESS_MSG


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        return save_error(NONPOSITIVE_VALUE_MSG)

    parsed_date = extract_date(income_date)
    if parsed_date is None:
        return save_error(INCORRECT_DATE_MSG)
    return save_income(amount, parsed_date)


def save_cost(category_name: str, amount: float, parsed_date: Date) -> str:
    financial_transactions_storage.append(
        {CATEGORY_KEY: category_name, AMOUNT_KEY: amount, DATE_KEY: parsed_date},
    )
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if amount <= 0:
        return save_error(NONPOSITIVE_VALUE_MSG)

    parsed_date = extract_date(income_date)
    if parsed_date is None:
        return save_error(INCORRECT_DATE_MSG)

    if not is_valid_category(category_name):
        return save_error(NOT_EXISTS_CATEGORY)
    return save_cost(category_name, amount, parsed_date)


def cost_categories_handler() -> str:
    categories: list[str] = []
    for common_category, target_categories in EXPENSE_CATEGORIES.items():
        categories.extend(f"{common_category}::{target_category}" for target_category in target_categories)
    return "\n".join(categories)


def is_before(date_left: Date, date_right: Date) -> bool:
    return date_to_comparable(date_left) < date_to_comparable(date_right)


def update_category_details(category_details: dict[str, float], category: str, amount: float) -> None:
    if category not in category_details:
        category_details[category] = ZERO_AMOUNT
    category_details[category] += amount


def handle_stats_item(
    item: dict[str, Any],
    report_date: Date,
    category_details: dict[str, float],
) -> tuple[float, float]:
    item_date = item.get(DATE_KEY)
    if not item or item_date is None or not is_before(item_date, report_date):
        return ZERO_AMOUNT, ZERO_AMOUNT
    amount = item.get(AMOUNT_KEY)
    if amount is None:
        return ZERO_AMOUNT, ZERO_AMOUNT
    category = item.get(CATEGORY_KEY)
    if category is None:
        return ZERO_AMOUNT, amount
    update_category_details(category_details, category, amount)
    return amount, ZERO_AMOUNT


def collect_stats(report_date: Date) -> tuple[float, float, dict[str, float]]:
    costs_amount = ZERO_AMOUNT
    incomes_amount = ZERO_AMOUNT
    category_details: dict[str, float] = {}

    for item in financial_transactions_storage:
        item_costs, item_incomes = handle_stats_item(item, report_date, category_details)
        costs_amount += item_costs
        incomes_amount += item_incomes
    return costs_amount, incomes_amount, category_details


def render_details(category_details: dict[str, float]) -> str:
    details = []
    for index, (category, amount) in enumerate(category_details.items()):
        details.append(f"{index}. {category}: {amount}")
    return "\n".join(details)


def stats_handler(report_date: str) -> str:
    parsed_report_date = extract_date(report_date)
    if parsed_report_date is None:
        return INCORRECT_DATE_MSG

    costs_amount, incomes_amount, category_details = collect_stats(parsed_report_date)
    total_capital = costs_amount - incomes_amount
    amount_word = "loss" if total_capital < 0 else "profit"

    return (
        f"Your statistics as of {report_date}:\n"
        f"Total capital: {total_capital:.2f} rubles\n"
        f"This month, the {amount_word} amounted to {total_capital:.2f} rubles.\n"
        f"Income: {costs_amount:.2f} rubles\n"
        f"Expenses: {incomes_amount:.2f} rubles\n\n"
        f"Details (category: amount):\n"
        f"{render_details(category_details)}\n"
    )


def parse_amount(raw_amount: str) -> float:
    return float(raw_amount.replace(",", "."))


def handle_income_command(command_parts: list[str]) -> str:
    if len(command_parts) != DATE_PARTS_COUNT:
        return UNKNOWN_COMMAND_MSG
    amount = parse_amount(command_parts[1])
    return income_handler(amount, command_parts[2])


def handle_cost_command(command_parts: list[str]) -> str:
    if len(command_parts) == DAY_LEN and command_parts[1] == "categories":
        return cost_categories_handler()
    if len(command_parts) != YEAR_LEN:
        return UNKNOWN_COMMAND_MSG
    amount = parse_amount(command_parts[2])
    result = cost_handler(command_parts[1], amount, command_parts[3])
    if result == NOT_EXISTS_CATEGORY:
        return f"{result}\n{cost_categories_handler()}"
    return result


def handle_command(command: str) -> str:
    command_parts = command.split()
    if not command_parts:
        return UNKNOWN_COMMAND_MSG
    if command_parts[0] == "income":
        return handle_income_command(command_parts)
    if command_parts[0] == "cost":
        return handle_cost_command(command_parts)
    if command_parts[0] == "stats" and len(command_parts) == DAY_LEN:
        return stats_handler(command_parts[1])
    return UNKNOWN_COMMAND_MSG


def main() -> None:
    command = input()
    while command:
        if command == "exit":
            return
        print(handle_command(command))
        command = input()


if __name__ == "__main__":
    main()
