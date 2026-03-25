#!/usr/bin/env python

from dataclasses import dataclass, field
from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

NUMBER_OF_MONTHS = 12
DATE_PARTS_COUNT = 3
CATEGORY_PARTS_COUNT = 2
FEBRUARY = 2
LEAP_YEAR_FEBRUARY_DAYS = 29
INCOME_ARGS_COUNT = 3
STATS_ARGS_COUNT = 2
COST_ARGS_COUNT = 4
DECIMAL_DIGITS = 2

ZERO_AMOUNT = 0

KEY_OPERATION_TYPE = "operation_type"
KEY_CATEGORY = "category"
KEY_AMOUNT = "amount"
KEY_DATE = "date"
OPERATION_INCOME = "income"
OPERATION_COST = "cost"

NUMBER_OF_DAYS_IN_MONTH = {
    1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31,
}

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


@dataclass
class StatsData:
    costs_amount: float = float(ZERO_AMOUNT)
    incomes_amount: float = float(ZERO_AMOUNT)
    expenses_by_categories: dict[str, float] = field(default_factory=dict)


DateTuple = tuple[int, int, int]


def add_error_stub() -> None:
    financial_transactions_storage.append({})


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    divisible_by_four = year % 4 == 0
    not_divisible_by_hundred = year % 100 != 0
    divisible_by_four_hundred = year % 400 == 0
    return (divisible_by_four and not_divisible_by_hundred) or divisible_by_four_hundred


def parse_raw_date(maybe_dt: str) -> DateTuple | None:
    date_parts = maybe_dt.split("-")
    if len(date_parts) != DATE_PARTS_COUNT:
        return None
    if not all(part.isdigit() for part in date_parts):
        return None
    day, month, year = (int(part) for part in date_parts)
    return day, month, year


def extract_date(maybe_dt: str) -> DateTuple | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: tuple формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """

    raw_date = parse_raw_date(maybe_dt)
    if raw_date is None:
        return None

    day, month, year = raw_date
    if month < 1 or month > NUMBER_OF_MONTHS or year < 0:
        return None
    if is_leap_year(year) and month == FEBRUARY and 1 <= day <= LEAP_YEAR_FEBRUARY_DAYS:
        return raw_date
    if 1 <= day <= NUMBER_OF_DAYS_IN_MONTH[month]:
        return raw_date
    return None


def valid_date(maybe_dt: str) -> bool:
    return extract_date(maybe_dt) is not None


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        add_error_stub()
        return NONPOSITIVE_VALUE_MSG
    parsed_income_date = extract_date(income_date)
    if parsed_income_date is None:
        add_error_stub()
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append(
        {
            KEY_OPERATION_TYPE: OPERATION_INCOME,
            KEY_AMOUNT: amount,
            KEY_DATE: parsed_income_date,
        }
    )
    return OP_SUCCESS_MSG


def parse_category(category_name: str) -> tuple[str, str] | None:
    category_parts = category_name.split("::")
    if len(category_parts) != CATEGORY_PARTS_COUNT:
        return None
    return category_parts[0], category_parts[1]


def cost_handler(category_name: str, amount: float, cost_date: str) -> str:
    if amount <= 0:
        add_error_stub()
        return NONPOSITIVE_VALUE_MSG
    parsed_cost_date = extract_date(cost_date)
    if parsed_cost_date is None:
        add_error_stub()
        return INCORRECT_DATE_MSG
    parsed_category = parse_category(category_name)
    if parsed_category is None:
        add_error_stub()
        return NOT_EXISTS_CATEGORY
    common_category, target_category = parsed_category
    if common_category not in EXPENSE_CATEGORIES or target_category not in EXPENSE_CATEGORIES[common_category]:
        add_error_stub()
        return NOT_EXISTS_CATEGORY

    financial_transactions_storage.append(
        {
            KEY_OPERATION_TYPE: OPERATION_COST,
            KEY_CATEGORY: category_name,
            KEY_AMOUNT: amount,
            KEY_DATE: parsed_cost_date,
        }
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    all_categories: list[str] = []
    for common_category, target_categories in EXPENSE_CATEGORIES.items():
        all_categories.extend(f"{common_category}::{target_category}" for target_category in target_categories)
    return "\n".join(all_categories)


def stats_handler(report_date: str) -> str:
    if extract_date(report_date) is None:
        return INCORRECT_DATE_MSG
    return form_stats_answer(report_date, count_stats_for_date(report_date))


def record_date(record: dict[str, Any]) -> DateTuple | None:
    raw_date = record.get(KEY_DATE)
    if isinstance(raw_date, tuple):
        return raw_date
    if isinstance(raw_date, str):
        return extract_date(raw_date)
    return None


def is_same_month(date: DateTuple, target_date: DateTuple) -> bool:
    month, year = date[1], date[2]
    target_month, target_year = target_date[1], target_date[2]
    same_month = month == target_month
    same_year = year == target_year
    return same_month and same_year


def normalize_amount(value: Any) -> float:
    if isinstance(value, (float, int)):
        return float(value)
    return ZERO_AMOUNT


def is_cost_record(record: dict[str, Any]) -> bool:
    operation_type = record.get(KEY_OPERATION_TYPE)
    return operation_type == OPERATION_COST or (operation_type is None and KEY_CATEGORY in record)


def add_cost_to_stats(stats: StatsData, record: dict[str, Any], amount: float) -> None:
    stats.costs_amount += amount
    raw_category = record.get(KEY_CATEGORY)
    if not isinstance(raw_category, str) or not raw_category:
        return
    previous_value = stats.expenses_by_categories.get(raw_category, float(ZERO_AMOUNT))
    stats.expenses_by_categories[raw_category] = previous_value + amount


def round_stats(stats: StatsData) -> None:
    stats.costs_amount = round(stats.costs_amount, DECIMAL_DIGITS)
    stats.incomes_amount = round(stats.incomes_amount, DECIMAL_DIGITS)
    for category_name, category_amount in stats.expenses_by_categories.items():
        stats.expenses_by_categories[category_name] = round(category_amount, DECIMAL_DIGITS)


def init_stats() -> StatsData:
    return StatsData()


def should_skip_record(current_date: DateTuple | None, report_date_tuple: DateTuple) -> bool:
    if current_date is None:
        return True
    if not is_tuple_date_before(current_date, report_date_tuple):
        return True
    return not is_same_month(current_date, report_date_tuple)


def count_stats_for_date(report_date: str) -> StatsData:
    report_date_tuple = extract_date(report_date)
    if report_date_tuple is None:
        return init_stats()

    stats = init_stats()
    for record in financial_transactions_storage:
        if not record:
            continue
        current_date = record_date(record)
        if should_skip_record(current_date, report_date_tuple):
            continue

        amount = normalize_amount(record.get(KEY_AMOUNT))
        if is_cost_record(record):
            add_cost_to_stats(stats, record, amount)
        else:
            stats.incomes_amount += amount

    round_stats(stats)
    return stats


def is_tuple_date_before(date: DateTuple, target_date: DateTuple) -> bool:
    converted_date = (date[2], date[1], date[0])
    converted_target_date = (target_date[2], target_date[1], target_date[0])
    return converted_date <= converted_target_date


def is_date_before(date: str, target_date: str) -> bool:
    source_date = extract_date(date)
    target_date_parsed = extract_date(target_date)
    if source_date is None or target_date_parsed is None:
        return False
    return is_tuple_date_before(source_date, target_date_parsed)


def form_stats_answer(report_date: str, stats: StatsData) -> str:
    total_capital = round(stats.costs_amount - stats.incomes_amount, DECIMAL_DIGITS)
    amount_word = "loss" if total_capital < 0 else "profit"

    category_details_lines: list[str] = []
    for index, (category, amount) in enumerate(stats.expenses_by_categories.items()):
        category_details_lines.append(f"{index}. {category}: {amount}")
    category_details_stat = "\n".join(category_details_lines)

    return f"""Your statistics as of {report_date}:
Total capital: {total_capital} rubles
This month, the {amount_word} amounted to {total_capital} rubles.
Income: {stats.costs_amount} rubles
Expenses: {stats.incomes_amount} rubles

Details (category: amount):
{category_details_stat}
"""


def handle_income_command(args: tuple[str, ...]) -> str:
    if len(args) != INCOME_ARGS_COUNT:
        return UNKNOWN_COMMAND_MSG
    amount = parse_amount(args[1])
    if amount is None:
        return UNKNOWN_COMMAND_MSG
    return income_handler(amount, args[2])


def handle_cost_command(args: tuple[str, ...]) -> str:
    if len(args) == STATS_ARGS_COUNT and args[1] == "categories":
        return cost_categories_handler()
    if len(args) != COST_ARGS_COUNT:
        return UNKNOWN_COMMAND_MSG
    amount = parse_amount(args[2])
    if amount is None:
        return UNKNOWN_COMMAND_MSG
    return cost_handler(args[1], amount, args[3])


def handle_stats_command(args: tuple[str, ...]) -> str:
    if len(args) != STATS_ARGS_COUNT:
        return UNKNOWN_COMMAND_MSG
    return stats_handler(args[1])


def process_command(*args: str) -> None:
    if not args:
        print(UNKNOWN_COMMAND_MSG)
        return

    command = args[0]
    match command:
        case "income":
            message = handle_income_command(args)
        case "cost":
            message = handle_cost_command(args)
        case "stats":
            message = handle_stats_command(args)
        case _:
            message = UNKNOWN_COMMAND_MSG
    print(message)


def string_to_float(string: str) -> float:
    return float(string.replace(",", "."))


def parse_amount(raw_amount: str) -> float | None:
    amount = raw_amount.replace(",", ".")
    if not amount:
        return None
    body = amount[1:] if amount[0] in "+-" else amount
    valid_body = bool(body) and body != "."
    valid_dots = body.count(".") <= 1
    valid_symbols = all(ch.isdigit() or ch == "." for ch in body)
    if valid_body and valid_dots and valid_symbols:
        return string_to_float(raw_amount)
    return None


def main() -> None:
    """Ваш код здесь"""
    request = input()
    while request:
        elements = request.split()
        process_command(*elements)
        request = input()


if __name__ == "__main__":
    main()
