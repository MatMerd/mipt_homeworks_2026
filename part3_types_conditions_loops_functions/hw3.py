#!/usr/bin/env python3

import sys
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

TRANSACTION_AMOUNT_KEY = "amount"
TRANSACTION_DATE_KEY = "date"
TRANSACTION_CATEGORY_KEY = "category"


EXPENSE_CATEGORIES = MappingProxyType({
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": (),
})


financial_transactions_storage: list[dict[str, Any] | None] = []

DATE_SPLIT_COUNT = 3
MIN_MONTH = 1
MAX_MONTH = 12
MIN_DAY = 1
MAX_DAYS_LONG = 31
MAX_DAYS_SHORT = 30
MAX_DAYS_FEB_LEAP = 29
MAX_DAYS_FEB = 28
MONTHS_LONG = (1, 3, 5, 7, 8, 10, 12)
MONTHS_SHORT = (4, 6, 9, 11)
FEBRUARY = 2

TWO = 2
THREE = 3
FOUR = 4


DateType = tuple[int, int, int]


@dataclass
class StatsAccumulator:
    total_capital: float = 0
    month_income: float = 0
    month_expenses: float = 0
    details: dict[str, float] = field(default_factory=dict)


def _reject_transaction(error_message: str) -> str:
    financial_transactions_storage.append(None)
    return error_message


def _max_days_in_month(month: int, year: int) -> int:
    if month in MONTHS_LONG:
        return MAX_DAYS_LONG
    if month in MONTHS_SHORT:
        return MAX_DAYS_SHORT
    if month == FEBRUARY and is_leap_year(year):
        return MAX_DAYS_FEB_LEAP
    return MAX_DAYS_FEB


def _is_month_match(transaction_date: DateType, report_date: DateType) -> bool:
    return transaction_date[1] == report_date[1]


def _collect_transaction_stats(report_date: DateType) -> StatsAccumulator:
    stats = StatsAccumulator()
    for transaction in financial_transactions_storage:
        if not transaction or not date_le(transaction[TRANSACTION_DATE_KEY], report_date):
            continue
        if TRANSACTION_CATEGORY_KEY in transaction:
            _collect_cost_stats(stats, transaction, report_date)
            continue
        _collect_income_stats(stats, transaction, report_date)
    return stats


def _collect_cost_stats(stats: StatsAccumulator, transaction: dict[str, Any], report_date: DateType) -> None:
    amount = transaction[TRANSACTION_AMOUNT_KEY]
    stats.total_capital -= amount
    if _is_month_match(transaction[TRANSACTION_DATE_KEY], report_date):
        stats.month_expenses += amount
        category = transaction[TRANSACTION_CATEGORY_KEY]
        stats.details[category] = stats.details.get(category, 0) + amount


def _collect_income_stats(stats: StatsAccumulator, transaction: dict[str, Any], report_date: DateType) -> None:
    amount = transaction[TRANSACTION_AMOUNT_KEY]
    stats.total_capital += amount
    if _is_month_match(transaction[TRANSACTION_DATE_KEY], report_date):
        stats.month_income += amount


def _format_detail_lines(details: dict[str, float]) -> list[str]:
    sorted_details = sorted(details.items())
    return [
        f"{count}. {category}: {amount}"
        for count, (category, amount) in enumerate(sorted_details, start=1)
    ]


def _format_stats(date: DateType, stats: StatsAccumulator) -> str:
    month_type = "loss" if stats.month_income < stats.month_expenses else "profit"
    month_balance = abs(stats.month_income - stats.month_expenses)
    details_lines = _format_detail_lines(stats.details)
    lines = [
        f"Your statistics as of {date[0]}-{date[1]}-{date[2]}:",
        f"Total capital: {stats.total_capital} rubles",
        f"This month, the {month_type} amounted to {month_balance} rubles.",
        f"Income: {stats.month_income} rubles",
        f"Expenses: {stats.month_expenses} rubles",
        "Details (category: amount):",
        *details_lines,
    ]
    return "\n".join(lines)


def _parse_amount(raw_value: str) -> float:
    return float(raw_value.replace(",", "."))


def _has_valid_date_parts(raw_date_parts: list[str]) -> bool:
    if len(raw_date_parts) != DATE_SPLIT_COUNT:
        return False
    return all(part.isdigit() for part in raw_date_parts)


def _handle_cost_command(command: list[str]) -> str:
    if len(command) == TWO and command[1] == "categories":
        return cost_categories_handler()
    if len(command) == FOUR:
        return cost_handler(command[1], _parse_amount(command[2]), command[3])
    return UNKNOWN_COMMAND_MSG


def _execute_command(command: list[str]) -> str:
    operation = command[0]
    if operation == "income" and len(command) == THREE:
        return income_handler(_parse_amount(command[1]), command[2])
    if operation == "cost":
        return _handle_cost_command(command)
    if operation == "stats" and len(command) == TWO:
        return stats_handler(command[1])
    return UNKNOWN_COMMAND_MSG


def is_leap_year(year: int) -> bool:
    divisible_by_four = year % 4 == 0
    divisible_by_hundred = year % 100 == 0
    divisible_by_four_hundred = year % 400 == 0
    return bool((divisible_by_four and not divisible_by_hundred) or divisible_by_four_hundred)


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    raw_date_parts = maybe_dt.split("-")
    if not _has_valid_date_parts(raw_date_parts):
        return None
    day, month, year = (int(part) for part in raw_date_parts)
    date: DateType = (day, month, year)
    day, month, year = date
    if not (MIN_MONTH <= month <= MAX_MONTH and day >= MIN_DAY):
        return None
    return date if day <= _max_days_in_month(month, year) else None


def date_le(date1: DateType, date2: DateType) -> bool:
    year_and_month_and_day1 = (date1[2], date1[1], date1[0])
    year_and_month_and_day2 = (date2[2], date2[1], date2[0])
    return year_and_month_and_day1 <= year_and_month_and_day2


def income_handler(amount: float, income_date: str) -> str:
    date = extract_date(income_date)
    if amount <= 0:
        return _reject_transaction(NONPOSITIVE_VALUE_MSG)
    if date is None:
        return _reject_transaction(INCORRECT_DATE_MSG)
    financial_transactions_storage.append({
        TRANSACTION_AMOUNT_KEY: amount,
        TRANSACTION_DATE_KEY: date,
    })
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    date = extract_date(income_date)
    if amount <= 0:
        return _reject_transaction(NONPOSITIVE_VALUE_MSG)

    if date is None:
        return _reject_transaction(INCORRECT_DATE_MSG)
    contains_separator = category_name.count("::") == 1
    if not (contains_separator and all(part for part in category_name.split("::"))):
        return _reject_transaction(NOT_EXISTS_CATEGORY)

    common_category, target_category = category_name.split("::")

    if common_category not in EXPENSE_CATEGORIES or target_category not in EXPENSE_CATEGORIES[common_category]:
        return _reject_transaction(f"{NOT_EXISTS_CATEGORY}\n{cost_categories_handler()}")

    financial_transactions_storage.append({
        TRANSACTION_CATEGORY_KEY: category_name,
        TRANSACTION_AMOUNT_KEY: amount,
        TRANSACTION_DATE_KEY: date,
    })
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return "\n".join(f"{common_category}::{target_category}"
                     for common_category, target_categories in EXPENSE_CATEGORIES.items()
                     for target_category in target_categories)


def stats_handler(report_date: str) -> str:
    date = extract_date(report_date)
    if date is None:
        return INCORRECT_DATE_MSG
    stats = _collect_transaction_stats(date)
    return _format_stats(date, stats)


def main() -> None:
    for raw_input in sys.stdin:
        command = raw_input.split()
        if not command:
            continue
        print(_execute_command(command))


if __name__ == "__main__":
    main()
