#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"
STATS_TITLE_PREFIX = "Your statistics as of"
TOTAL_CAPITAL_TITLE = "Total capital"
PROFIT_TEXT = "This month, the profit amounted to"
LOSS_TEXT = "This month, the loss amounted to"
INCOME_TITLE = "Income"
EXPENSES_TITLE = "Expenses"
DETAILS_TITLE = "Details (category: amount):"
RUBLES_TEXT = "rubles"
INCOME_KIND = "income"
COST_KIND = "cost"
CATEGORY_SEPARATOR = "::"
CATEGORY_PARTS_COUNT = 2
INCOME_COMMAND = INCOME_KIND
COST_COMMAND = COST_KIND
STATS_COMMAND = "stats"
STATS_CAPITAL_KEY = "capital"
STATS_INCOME_KEY = "income"
STATS_COST_KEY = "cost"
STATS_DETAILS_KEY = "details"

DATE_SEPARATOR = "-"
DATE_PARTS_COUNT = 3
DAY_PART_LEN = 2
YEAR_PART_LEN = 4
MIN_DAY = 1
MIN_MONTH = 1
MAX_MONTH = 12
FEBRUARY = 2
DAYS_IN_SHORT_FEBRUARY = 28
DAYS_IN_LEAP_FEBRUARY = 29
DAYS_IN_MEDIUM_MONTH = 30
DAYS_IN_LONG_MONTH = 31
MEDIUM_MONTHS = (4, 6, 9, 11)

INCOME_COMMAND_PARTS_COUNT = 3
COST_COMMAND_PARTS_COUNT = 4
STATS_COMMAND_PARTS_COUNT = 2


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


DateTuple = tuple[int, int, int]
Transaction = dict[str, Any]
CategoryTotals = dict[str, float]
StatsAccumulator = dict[str, Any]


financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    if year % 4 != 0:
        return False
    if year % 100 != 0:
        return True
    return year % 400 == 0


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    date_parts = maybe_dt.split(DATE_SEPARATOR)
    if len(date_parts) != DATE_PARTS_COUNT:
        return None

    if not is_valid_date_text_parts(date_parts[0], date_parts[1], date_parts[2]):
        return None

    return parse_date_parts(date_parts)


def parse_date_parts(date_parts: list[str]) -> DateTuple | None:
    day = int(date_parts[0])
    month = int(date_parts[1])
    year = int(date_parts[2])
    if month < MIN_MONTH or month > MAX_MONTH:
        return None

    if day < MIN_DAY or day > days_in_month(month, year):
        return None

    return day, month, year


def is_valid_date_text_parts(day_text: str, month_text: str, year_text: str) -> bool:
    if not day_text.isdigit() or not month_text.isdigit() or not year_text.isdigit():
        return False

    return (len(day_text), len(month_text), len(year_text)) == (
        DAY_PART_LEN,
        DAY_PART_LEN,
        YEAR_PART_LEN,
    )


def days_in_month(month: int, year: int) -> int:
    if month == FEBRUARY:
        if is_leap_year(year):
            return DAYS_IN_LEAP_FEBRUARY
        return DAYS_IN_SHORT_FEBRUARY

    if month in MEDIUM_MONTHS:
        return DAYS_IN_MEDIUM_MONTH

    return DAYS_IN_LONG_MONTH


def append_invalid_transaction() -> None:
    financial_transactions_storage.append({})


def append_income_transaction(amount: float, income_date: DateTuple) -> None:
    financial_transactions_storage.append(
        {
            "kind": INCOME_KIND,
            "amount": amount,
            "date": income_date,
        }
    )


def append_cost_transaction(category_name: str, amount: float, income_date: DateTuple) -> None:
    financial_transactions_storage.append(
        {
            "kind": COST_KIND,
            "category": category_name,
            "amount": amount,
            "date": income_date,
        }
    )


def income_handler(amount: float, income_date: str) -> str:
    if amount <= float(0):
        append_invalid_transaction()
        return NONPOSITIVE_VALUE_MSG

    date_data = extract_date(income_date)
    if date_data is None:
        append_invalid_transaction()
        return INCORRECT_DATE_MSG

    append_income_transaction(amount, date_data)
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if not is_valid_expense_category(category_name):
        append_invalid_transaction()
        return NOT_EXISTS_CATEGORY

    if amount <= float(0):
        append_invalid_transaction()
        return NONPOSITIVE_VALUE_MSG

    date_data = extract_date(income_date)
    if date_data is None:
        append_invalid_transaction()
        return INCORRECT_DATE_MSG

    append_cost_transaction(category_name, amount, date_data)
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return "\n".join(
        f"{common_category}{CATEGORY_SEPARATOR}{target_category}"
        for common_category, category_items in EXPENSE_CATEGORIES.items()
        for target_category in category_items
    )


def stats_handler(report_date: str) -> str:
    report_date_data = extract_date(report_date)
    if report_date_data is None:
        return INCORRECT_DATE_MSG

    stats_data = collect_stats(report_date_data)
    return format_stats_report(report_date, stats_data)


def format_stats_report(report_date: str, stats_data: tuple[float, float, float, CategoryTotals]) -> str:
    capital, current_income, current_cost, details = stats_data
    stats_lines = [
        f"{STATS_TITLE_PREFIX} {report_date}:",
        f"{TOTAL_CAPITAL_TITLE}: {capital} {RUBLES_TEXT}",
        format_profit_or_loss(capital),
        f"{INCOME_TITLE}: {current_cost} {RUBLES_TEXT}",
        f"{EXPENSES_TITLE}: {current_income} {RUBLES_TEXT}",
        "",
        DETAILS_TITLE,
    ]
    stats_lines.extend(format_details_lines(details))
    stats_lines.append("")
    return "\n".join(stats_lines)


def is_valid_expense_category(category_name: str) -> bool:
    category_parts = category_name.split(CATEGORY_SEPARATOR)
    if len(category_parts) != CATEGORY_PARTS_COUNT:
        return False

    common_category, target_category = category_parts[0], category_parts[1]
    if common_category not in EXPENSE_CATEGORIES:
        return False

    return target_category in EXPENSE_CATEGORIES[common_category]


def collect_stats(report_date: DateTuple) -> tuple[float, float, float, CategoryTotals]:
    accumulator = create_stats_accumulator()
    target_date = make_sortable_date(report_date)

    for transaction in financial_transactions_storage:
        operation = transaction_to_operation(transaction)
        if operation is None:
            continue

        process_operation_for_stats(operation, target_date, accumulator)

    current_income = round(float(accumulator[STATS_INCOME_KEY]), 2)
    current_cost = round(float(accumulator[STATS_COST_KEY]), 2)
    return round(current_cost - current_income, 2), current_income, current_cost, accumulator[STATS_DETAILS_KEY]


def create_stats_accumulator() -> StatsAccumulator:
    return {
        STATS_CAPITAL_KEY: float(0),
        STATS_INCOME_KEY: float(0),
        STATS_COST_KEY: float(0),
        STATS_DETAILS_KEY: {},
    }


def make_sortable_date(date_data: DateTuple) -> DateTuple:
    return date_data[2], date_data[1], date_data[0]


def process_operation_for_stats(
    operation: tuple[float, DateTuple, str, str],
    target_date: DateTuple,
    accumulator: StatsAccumulator,
) -> None:
    amount, operation_date, category_name, kind = operation
    if make_sortable_date(operation_date) > target_date:
        return

    if kind == INCOME_KIND:
        accumulator[STATS_INCOME_KEY] += amount
        return

    accumulator[STATS_COST_KEY] += amount
    details = accumulator[STATS_DETAILS_KEY]
    details[category_name] = details.get(category_name, float(0)) + amount


def transaction_to_operation(transaction: Transaction) -> tuple[float, DateTuple, str, str] | None:
    transaction_kind = get_transaction_kind(transaction)

    transaction_amount = get_transaction_amount(transaction)
    if transaction_amount is None:
        return None

    transaction_date = get_transaction_date(transaction)
    if transaction_date is None:
        return None

    category = get_category_target_name(transaction.get("category")) if transaction_kind == COST_KIND else INCOME_KIND

    return transaction_amount, transaction_date, category, transaction_kind


def get_transaction_kind(transaction: Transaction) -> str:
    transaction_kind = transaction.get("kind")
    if isinstance(transaction_kind, str) and transaction_kind in {INCOME_KIND, COST_KIND}:
        return transaction_kind

    if isinstance(transaction.get("category"), str):
        return COST_KIND

    return INCOME_KIND


def get_transaction_amount(transaction: Transaction) -> float | None:
    transaction_amount = transaction.get("amount")
    if isinstance(transaction_amount, bool):
        return None

    if not isinstance(transaction_amount, (float, int)):
        return None

    return float(transaction_amount)


def get_transaction_date(transaction: Transaction) -> DateTuple | None:
    transaction_date = transaction.get("date")
    if isinstance(transaction_date, str):
        return extract_date(transaction_date)

    if not isinstance(transaction_date, tuple):
        return None

    if len(transaction_date) != DATE_PARTS_COUNT:
        return None

    day, month, year = transaction_date
    if not is_int_tuple(day, month, year):
        return None

    return day, month, year


def is_int_tuple(day: Any, month: Any, year: Any) -> bool:
    return isinstance(day, int) and isinstance(month, int) and isinstance(year, int)


def get_category_target_name(raw_category: Any) -> str:
    if not isinstance(raw_category, str):
        return ""

    return raw_category


def format_profit_or_loss(total_capital: float) -> str:
    amount_word = "loss" if total_capital < 0 else "profit"
    return f"This month, the {amount_word} amounted to {total_capital} {RUBLES_TEXT}."


def format_details_lines(details: CategoryTotals) -> list[str]:
    details_lines: list[str] = []
    for index, (category, amount) in enumerate(details.items()):
        details_lines.append(f"{index}. {category}: {amount}")

    return details_lines


def parse_amount(raw_amount: str) -> float | None:
    normalized_amount = raw_amount.replace(",", ".")
    if not is_valid_amount_text(normalized_amount):
        return None

    return float(normalized_amount)


def is_valid_amount_text(normalized_amount: str) -> bool:
    unsigned_amount = normalized_amount.removeprefix("-")
    if unsigned_amount == "":
        return False

    if unsigned_amount.count(".") > MIN_DAY:
        return False

    if "." not in unsigned_amount:
        return unsigned_amount.isdigit()

    return is_valid_float_amount_text(unsigned_amount)


def is_valid_float_amount_text(unsigned_amount: str) -> bool:
    left_part, right_part = unsigned_amount.split(".", 1)
    if left_part == "" and right_part == "":
        return False

    if not is_digit_or_empty(left_part):
        return False

    return is_digit_or_empty(right_part)


def is_digit_or_empty(part: str) -> bool:
    return part == "" or part.isdigit()


def handle_income_command(command_parts: list[str]) -> None:
    if len(command_parts) != INCOME_COMMAND_PARTS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount = parse_amount(command_parts[1])
    if amount is None:
        print(UNKNOWN_COMMAND_MSG)
        return

    print(income_handler(amount, command_parts[2]))


def handle_cost_command(command_parts: list[str]) -> None:
    if len(command_parts) == STATS_COMMAND_PARTS_COUNT and command_parts[1] == "categories":
        print(cost_categories_handler())
        return

    if len(command_parts) != COST_COMMAND_PARTS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount = parse_amount(command_parts[2])
    if amount is None:
        print(UNKNOWN_COMMAND_MSG)
        return

    command_result = cost_handler(command_parts[1], amount, command_parts[3])
    print(command_result)
    if command_result == NOT_EXISTS_CATEGORY:
        print(cost_categories_handler())


def handle_stats_command(command_parts: list[str]) -> None:
    if len(command_parts) != STATS_COMMAND_PARTS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return

    print(stats_handler(command_parts[1]))


def process_input_line(raw_line: str) -> None:
    command_parts = raw_line.split()
    if not command_parts:
        print(UNKNOWN_COMMAND_MSG)
        return

    handlers = {
        INCOME_COMMAND: handle_income_command,
        COST_COMMAND: handle_cost_command,
        STATS_COMMAND: handle_stats_command,
    }
    target_handler = handlers.get(command_parts[0])
    if target_handler is None:
        print(UNKNOWN_COMMAND_MSG)
        return

    target_handler(command_parts)


def main() -> None:
    """Ваш код здесь"""
    with open(0) as stdin:
        for line in stdin:
            process_input_line(line)


if __name__ == "__main__":
    main()
