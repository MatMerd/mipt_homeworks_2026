#!/usr/bin/env python3
from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

INCOME_CMD_PARTS = 3
COST_CMD_PARTS = 4
STATS_CMD_PARTS = 2
COST_CATEGORIES_CMD_PARTS = 2

MIN_DAY = 1
MIN_MONTH = 1
MAX_MONTH = 12
DATE_PARTS_COUNT = 3
DAY_TEXT_LEN = 2
MONTH_TEXT_LEN = 2
YEAR_TEXT_LEN = 4
FEBRUARY = 2
MONTHS_WITH_THIRTY_DAYS = (4, 6, 9, 11)
CATEGORY_PARTS_COUNT = 2

DateTuple = tuple[int, int, int]
StorageRecord = dict[str, Any]
StatsData = tuple[float, float, float, dict[str, float]]

KIND_KEY = "kind"
AMOUNT_KEY = "amount"
DATE_KEY = "date"
CATEGORY_KEY = "category"

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("Other",),
}


financial_transactions_storage: list[StorageRecord] = []


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0


def has_valid_date_lengths(day: str, month: str, year: str) -> bool:
    return (
        len(day),
        len(month),
        len(year),
    ) == (
        DAY_TEXT_LEN,
        MONTH_TEXT_LEN,
        YEAR_TEXT_LEN,
    )


def has_only_date_digits(day: str, month: str, year: str) -> bool:
    return day.isdigit() and month.isdigit() and year.isdigit()


def get_days_in_month(month: int, year: int) -> int:
    if month in MONTHS_WITH_THIRTY_DAYS:
        return 30
    if month == FEBRUARY:
        if is_leap_year(year):
            return 29
        return 28
    return 31


def has_valid_date_text(date_parts: list[str]) -> bool:
    day_text = date_parts[0]
    month_text = date_parts[1]
    year_text = date_parts[2]
    if not has_valid_date_lengths(day_text, month_text, year_text):
        return False
    return has_only_date_digits(day_text, month_text, year_text)


def to_date_tuple(date_parts: list[str]) -> DateTuple:
    day = int(date_parts[0])
    month = int(date_parts[1])
    year = int(date_parts[2])
    return day, month, year


def is_valid_date_tuple(date_tuple: DateTuple) -> bool:
    if date_tuple[1] < MIN_MONTH or date_tuple[1] > MAX_MONTH:
        return False
    if date_tuple[0] < MIN_DAY:
        return False
    return date_tuple[0] <= get_days_in_month(date_tuple[1], date_tuple[2])


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    date_parts = maybe_dt.split("-")
    if len(date_parts) != DATE_PARTS_COUNT:
        return None
    if not has_valid_date_text(date_parts):
        return None

    parsed_date = to_date_tuple(date_parts)
    if not is_valid_date_tuple(parsed_date):
        return None
    return parsed_date


def remove_sign(number_text: str) -> str:
    if number_text == "":
        return number_text
    if number_text[0] in "+-":
        return number_text[1:]
    return number_text


def is_unsigned_number(number_text: str) -> bool:
    if number_text == "":
        return False
    if number_text.count(".") > 1:
        return False
    if "." not in number_text:
        return number_text.isdigit()

    left, right = number_text.split(".", maxsplit=1)
    if left == "" and right == "":
        return False
    left_ok = left == "" or left.isdigit()
    right_ok = right == "" or right.isdigit()
    return left_ok and right_ok


def parse_amount(raw_amount: str) -> float | None:
    normalized = raw_amount.replace(",", ".")
    raw_number = remove_sign(normalized)
    if not is_unsigned_number(raw_number):
        return None
    return float(normalized)


def add_invalid_transaction() -> None:
    financial_transactions_storage.append({})


def is_valid_category(category_name: str) -> bool:
    if "::" not in category_name:
        return False
    category_parts = category_name.split("::")
    if len(category_parts) != CATEGORY_PARTS_COUNT:
        return False
    common_category = category_parts[0]
    target_category = category_parts[1]
    if common_category not in EXPENSE_CATEGORIES:
        return False
    return target_category in EXPENSE_CATEGORIES[common_category]


def income_handler(amount: float, income_date: str) -> str:
    parsed_date = extract_date(income_date)
    if amount <= 0:
        add_invalid_transaction()
        return NONPOSITIVE_VALUE_MSG
    if parsed_date is None:
        add_invalid_transaction()
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append(
        {
            KIND_KEY: "income",
            AMOUNT_KEY: amount,
            DATE_KEY: parsed_date,
        },
    )
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    parsed_date = extract_date(income_date)
    if amount <= 0:
        add_invalid_transaction()
        return NONPOSITIVE_VALUE_MSG
    if parsed_date is None:
        add_invalid_transaction()
        return INCORRECT_DATE_MSG
    if not is_valid_category(category_name):
        add_invalid_transaction()
        return NOT_EXISTS_CATEGORY

    financial_transactions_storage.append(
        {
            KIND_KEY: "cost",
            CATEGORY_KEY: category_name,
            AMOUNT_KEY: amount,
            DATE_KEY: parsed_date,
        },
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    category_lines: list[str] = []
    for common_category, targets in EXPENSE_CATEGORIES.items():
        category_lines.extend(f"{common_category}::{target_category}" for target_category in targets)
    return "\n".join(category_lines)


def to_key(date_info: DateTuple) -> tuple[int, int, int]:
    return date_info[2], date_info[1], date_info[0]


def is_not_later(record_date: DateTuple, report_date: DateTuple) -> bool:
    return to_key(record_date) <= to_key(report_date)


def is_in_report_month(record_date: DateTuple, report_date: DateTuple) -> bool:
    same_year = record_date[2] == report_date[2]
    same_month = record_date[1] == report_date[1]
    day_not_later = record_date[0] <= report_date[0]
    return same_year and same_month and day_not_later


def is_income_transaction(transaction: StorageRecord) -> bool:
    return bool(transaction) and transaction.get(KIND_KEY) == "income"


def is_cost_transaction(transaction: StorageRecord) -> bool:
    return bool(transaction) and transaction.get(KIND_KEY) == "cost"


def is_report_relevant(transaction: StorageRecord, report_date: DateTuple) -> bool:
    return is_not_later(transaction[DATE_KEY], report_date)


def get_cost_category_key(cost_category_name: str) -> str:
    category_parts = cost_category_name.split("::")
    return category_parts[1]


def add_category_amount(month_categories: dict[str, float], category_key: str, amount: float) -> None:
    current_amount = month_categories.get(category_key, float(0))
    month_categories[category_key] = current_amount + amount


def collect_income_totals(report_date: DateTuple) -> tuple[float, float]:
    total_income = float(0)
    month_income = float(0)
    for transaction in financial_transactions_storage:
        if not is_income_transaction(transaction):
            continue
        if not is_report_relevant(transaction, report_date):
            continue
        total_income += transaction[AMOUNT_KEY]
        if is_in_report_month(transaction[DATE_KEY], report_date):
            month_income += transaction[AMOUNT_KEY]
    return total_income, month_income


def collect_cost_totals(report_date: DateTuple) -> tuple[float, float, dict[str, float]]:
    total_cost = float(0)
    month_cost = float(0)
    month_categories: dict[str, float] = {}
    for transaction in financial_transactions_storage:
        if not is_cost_transaction(transaction):
            continue
        if not is_report_relevant(transaction, report_date):
            continue

        total_cost += transaction[AMOUNT_KEY]
        if is_in_report_month(transaction[DATE_KEY], report_date):
            month_cost += transaction[AMOUNT_KEY]
            category_key = get_cost_category_key(transaction[CATEGORY_KEY])
            add_category_amount(month_categories, category_key, transaction[AMOUNT_KEY])
    return total_cost, month_cost, month_categories


def build_transaction_stats(
    report_date: DateTuple,
) -> StatsData:
    total_income, month_income = collect_income_totals(report_date)
    total_cost, month_expenses, month_categories = collect_cost_totals(report_date)
    return total_income - total_cost, month_income, month_expenses, month_categories


def format_money(value: float) -> str:
    text = f"{value:.2f}"
    if text == "-0.00":
        return "0.00"
    return text


def format_money_for_details(value: float) -> str:
    return format_money(value).rstrip("0").rstrip(".")


def format_profit_or_loss(balance: float) -> str:
    amount_text = format_money(abs(balance))
    if balance >= 0:
        return f"This month, the profit amounted to {amount_text} rubles."
    return f"This month, the loss amounted to {amount_text} rubles."


def build_details_lines(month_categories: dict[str, float]) -> list[str]:
    detail_lines: list[str] = []
    counter = 1
    for category_name in sorted(month_categories):
        amount_text = format_money_for_details(month_categories[category_name])
        detail_lines.append(f"{counter}. {category_name}: {amount_text}")
        counter += 1
    return detail_lines


def build_month_balance(stats_data: StatsData) -> float:
    return stats_data[1] - stats_data[2]


def build_stats_report_lines(report_date: str, stats_data: StatsData) -> list[str]:
    balance = build_month_balance(stats_data)
    lines = [
        f"Your statistics as of {report_date}:",
        f"Total capital: {format_money(stats_data[0])} rubles",
        format_profit_or_loss(balance),
        f"Income: {format_money(stats_data[1])} rubles",
        f"Expenses: {format_money(stats_data[2])} rubles",
        "",
        "Details (category: amount):",
    ]
    lines.extend(build_details_lines(stats_data[3]))
    return lines


def stats_handler(report_date: str) -> str:
    parsed_report_date = extract_date(report_date)
    if parsed_report_date is None:
        return INCORRECT_DATE_MSG
    stats_data = build_transaction_stats(parsed_report_date)
    lines = build_stats_report_lines(report_date, stats_data)
    return "\n".join(lines)


def process_income_command(command_parts: list[str]) -> str:
    if len(command_parts) != INCOME_CMD_PARTS:
        return UNKNOWN_COMMAND_MSG
    amount = parse_amount(command_parts[1])
    if amount is None:
        return NONPOSITIVE_VALUE_MSG
    return income_handler(amount, command_parts[2])


def process_cost_command(command_parts: list[str]) -> str:
    if len(command_parts) == COST_CATEGORIES_CMD_PARTS and command_parts[1] == "categories":
        return cost_categories_handler()
    if len(command_parts) != COST_CMD_PARTS:
        return UNKNOWN_COMMAND_MSG

    amount = parse_amount(command_parts[2])
    if amount is None:
        return NONPOSITIVE_VALUE_MSG

    result = cost_handler(command_parts[1], amount, command_parts[3])
    if result != NOT_EXISTS_CATEGORY:
        return result
    categories_text = cost_categories_handler()
    return f"{NOT_EXISTS_CATEGORY}\n{categories_text}"


def process_stats_command(command_parts: list[str]) -> str:
    if len(command_parts) != STATS_CMD_PARTS:
        return UNKNOWN_COMMAND_MSG
    return stats_handler(command_parts[1])


def process_command(raw_line: str) -> str:
    line = raw_line.strip()
    if line == "":
        return ""

    command_parts = line.split()
    command = command_parts[0]
    if command == "income":
        return process_income_command(command_parts)
    if command == "cost":
        return process_cost_command(command_parts)
    if command == "stats":
        return process_stats_command(command_parts)
    return UNKNOWN_COMMAND_MSG


def main() -> None:
    """Ваш код здесь"""
    with open(0) as stdin:
        for raw_line in stdin:
            result = process_command(raw_line)
            if result == "":
                continue
            print(result)


if __name__ == "__main__":
    main()
