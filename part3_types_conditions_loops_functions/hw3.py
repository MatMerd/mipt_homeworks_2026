#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

INCOME_CMD = "income"
COST_CMD = "cost"
STATS_CMD = "stats"

EXIT_CMD = "exit"

Date = tuple[int, int, int]

MIN_MONTH = 1
MAX_MONTH = 12
MIN_DAY = 1
MIN_YEAR = 1

FEBRUARY = 2
DAYS_IN_LEAP_FEBRUARY = 29

DATE_LENGTH = 10
FIRST_SEPARATOR_INDEX = 2
SECOND_SEPARATOR_INDEX = 5
DATE_SEPARATOR = "-"

DAY_SLICE_END = 2
MONTH_SLICE_START = 3
MONTH_SLICE_END = 5
YEAR_SLICE_START = 6

CATEGORY_SEPARATOR = "::"

MONTH_DAYS_COMMON = {
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

INCOME_ARGS_COUNT = 2
COST_ARGS_COUNT = 3

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


def get_days_in_month(month: int, year: int) -> int:
    if month == FEBRUARY and is_leap_year(year):
        return DAYS_IN_LEAP_FEBRUARY
    return MONTH_DAYS_COMMON[month]


def is_valid_date_parts(day: int, month: int, year: int) -> bool:
    return (
        year >= MIN_YEAR
        and MIN_MONTH <= month <= MAX_MONTH
        and day >= MIN_DAY
        and day <= get_days_in_month(month, year)
    )


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: tuple формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    if (
        len(maybe_dt) != DATE_LENGTH
        or maybe_dt[FIRST_SEPARATOR_INDEX] != DATE_SEPARATOR
        or maybe_dt[SECOND_SEPARATOR_INDEX] != DATE_SEPARATOR
    ):
        return None

    parts = (
        maybe_dt[:DAY_SLICE_END],
        maybe_dt[MONTH_SLICE_START:MONTH_SLICE_END],
        maybe_dt[YEAR_SLICE_START:],
    )
    if not all(part.isdigit() for part in parts):
        return None

    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2])

    if not is_valid_date_parts(day, month, year):
        return None

    return day, month, year


def parse_amount(maybe_amount: str) -> float | None:
    """
    Парсит число из строки.
    :param str maybe_amount: Проверяемая строка
    :return: Число или None, если строка не число.
    :rtype: float | None
    """
    if maybe_amount == "":
        return None

    result = maybe_amount.replace(",", ".")
    if result.count(".") > 1:
        return None

    str_without_sign = result[1:] if result[0] in {"+-"} else result

    if str_without_sign in {"", "."} or result.endswith("."):
        return None

    if not all(ch.isdigit() or ch == "." for ch in str_without_sign):
        return None

    return float(result)


def split_category_name(category_name: str) -> tuple[str, str | None]:
    if CATEGORY_SEPARATOR not in category_name:
        return category_name, None

    if category_name.count(CATEGORY_SEPARATOR) != 1:
        return "", None

    separator_index = category_name.find(CATEGORY_SEPARATOR)
    common_category = category_name[:separator_index]
    target_category = category_name[separator_index + len(CATEGORY_SEPARATOR):]

    return common_category, target_category


def is_valid_category_name(category_name: str) -> bool:
    common_category, target_category = split_category_name(category_name)

    if common_category not in EXPENSE_CATEGORIES:
        return False

    target_categories = EXPENSE_CATEGORIES[common_category]

    if len(target_categories) == 0:
        return target_category is None

    if target_category is None:
        return False

    return target_category in target_categories


def build_available_categories() -> list[str]:
    categories: list[str] = []

    for common_category, target_categories in EXPENSE_CATEGORIES.items():
        if len(target_categories) == 0:
            categories.append(common_category)
        else:
            categories.extend(
                f"{common_category}{CATEGORY_SEPARATOR}{target_category}"
                for target_category in target_categories
            )

    return categories


def cost_categories_handler() -> str:
    return "\n".join(build_available_categories())


def build_category_error_message() -> str:
    categories_text = cost_categories_handler()
    return f"{NOT_EXISTS_CATEGORY}\n{categories_text}"


def format_money(amount: float) -> str:
    return f"{amount:.2f}"


def is_same_month(left: Date, right: Date) -> bool:
    return left[1:] == right[1:]


def is_date_not_later(left: Date, right: Date) -> bool:
    if left[2] != right[2]:
        return left[2] < right[2]

    if left[1] != right[1]:
        return left[1] < right[1]

    return left[0] <= right[0]


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
            "type": INCOME_CMD,
            "amount": amount,
            "date": parsed_date,
        }
    )
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if not is_valid_category_name(category_name):
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG
    parsed_date = extract_date(income_date)
    if parsed_date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append(
        {
            "type": COST_CMD,
            "category": category_name,
            "amount": amount,
            "date": parsed_date,
        }
    )
    return OP_SUCCESS_MSG


def get_detail_name(category_name: str) -> str:
    common_category, target_category = split_category_name(category_name)

    if target_category is None:
        return common_category

    return target_category


def add_amount_by_category(
    details_map: dict[str, float],
    category_name: str,
    amount: float,
) -> None:
    if category_name not in details_map:
        details_map[category_name] = 0

    details_map[category_name] += amount


def process_income_stats(
    amount: float,
    *,
    same_month: bool,
    stats_data: dict[str, Any],
) -> None:
    stats_data["total_income"] += amount
    if same_month:
        stats_data["month_income"] += amount


def process_cost_stats(
    transaction: dict[str, Any],
    amount: float,
    *,
    same_month: bool,
    stats_data: dict[str, Any],
) -> None:
    stats_data["total_expenses"] += amount
    if same_month:
        stats_data["month_expenses"] += amount

        category_name = transaction.get("category")
        if isinstance(category_name, str):
            add_amount_by_category(stats_data["details_map"], category_name, amount)


def extract_transaction_data(
    transaction: dict[str, Any],
) -> tuple[Date, float, str]:
    return (
        transaction["date"],
        float(transaction["amount"]),
        transaction["type"],
    )


def collect_stats_data(report_date_parts: Date) -> dict[str, Any]:
    stats_data = {
        "total_income": 0,
        "total_expenses": 0,
        "month_income": 0,
        "month_expenses": 0,
        "details_map": {},
    }

    for transaction in financial_transactions_storage:
        transaction_date, amount, transaction_type = extract_transaction_data(transaction)

        if not is_date_not_later(transaction_date, report_date_parts):
            continue

        if transaction_type == INCOME_CMD:
            process_income_stats(
                amount,
                same_month=is_same_month(transaction_date, report_date_parts),
                stats_data=stats_data,
            )
        elif transaction_type == COST_CMD:
            process_cost_stats(
                transaction,
                amount,
                same_month=is_same_month(transaction_date, report_date_parts),
                stats_data=stats_data,
            )

    return stats_data


def build_month_result_line(month_income: float, month_expenses: float) -> str:
    month_result = month_income - month_expenses

    if month_result >= 0:
        return f"This month, the profit amounted to {format_money(month_result)} rubles."

    return f"This month, the loss amounted to {format_money(-month_result)} rubles."


def build_details_lines(details_map: dict[str, float]) -> list[str]:
    lines: list[str] = []

    for index, category_name in enumerate(sorted(details_map.keys()), start=1):
        detail_name = get_detail_name(category_name)
        lines.append(
            f"{index}. {detail_name}: {format_money(details_map[category_name])}"
        )

    return lines


def build_stats_lines(
    report_date: str,
    total_capital: float,
    month_income: float,
    month_expenses: float,
    details_map: dict[str, float],
) -> list[str]:
    lines = [
        f"Your statistics as of {report_date}:",
        f"Total capital: {format_money(total_capital)} rubles",
        build_month_result_line(month_income, month_expenses),
        f"Income: {format_money(month_income)} rubles",
        f"Expenses: {format_money(month_expenses)} rubles",
        "",
        "Details (category: amount):",
    ]

    lines.extend(build_details_lines(details_map))
    return lines


def stats_handler(report_date: str) -> str:
    report_date_parts = extract_date(report_date)
    if report_date_parts is None:
        return INCORRECT_DATE_MSG

    stats_data = collect_stats_data(report_date_parts)

    total_capital = stats_data["total_income"] - stats_data["total_expenses"]

    lines = build_stats_lines(
        report_date,
        total_capital,
        stats_data["month_income"],
        stats_data["month_expenses"],
        stats_data["details_map"],
    )
    return "\n".join(lines)


def handle_income_command(command_args: list[str]) -> str:
    if len(command_args) != INCOME_ARGS_COUNT:
        return UNKNOWN_COMMAND_MSG

    amount_text = command_args[0]
    income_date = command_args[1]

    amount = parse_amount(amount_text)
    if amount is None:
        return UNKNOWN_COMMAND_MSG

    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    if extract_date(income_date) is None:
        return INCORRECT_DATE_MSG

    return income_handler(amount, income_date)


def validate_cost_command(
    category_name: str,
    amount_text: str,
    cost_date: str,
) -> tuple[float | None, str | None]:
    if not is_valid_category_name(category_name):
        return None, build_category_error_message()

    amount = parse_amount(amount_text)
    if amount is None:
        return None, UNKNOWN_COMMAND_MSG

    if amount <= 0:
        return None, NONPOSITIVE_VALUE_MSG

    if extract_date(cost_date) is None:
        return None, INCORRECT_DATE_MSG

    return amount, None


def handle_cost_command(command_args: list[str]) -> str:
    if len(command_args) == 1 and command_args[0] == "categories":
        return cost_categories_handler()

    if len(command_args) != COST_ARGS_COUNT:
        return UNKNOWN_COMMAND_MSG

    category_name = command_args[0]
    amount_text = command_args[1]
    cost_date = command_args[2]

    amount, error_message = validate_cost_command(
        category_name,
        amount_text,
        cost_date,
    )
    if error_message is not None:
        return error_message

    if amount is None:
        return UNKNOWN_COMMAND_MSG

    return cost_handler(category_name, amount, cost_date)


def handle_stats_command(command_args: list[str]) -> str:
    if len(command_args) != 1:
        return UNKNOWN_COMMAND_MSG

    report_date = command_args[0]
    if extract_date(report_date) is None:
        return INCORRECT_DATE_MSG

    return stats_handler(report_date)


COMMAND_HANDLERS = {
    INCOME_CMD: handle_income_command,
    COST_CMD: handle_cost_command,
    STATS_CMD: handle_stats_command,
}


def parse_command_line(command_line: str) -> tuple[str, list[str]] | None:
    parts = command_line.split()
    if len(parts) == 0:
        return None

    return parts[0], parts[1:]


def get_command_handler(command_name: str) -> Any | None:
    if command_name not in COMMAND_HANDLERS:
        return None

    return COMMAND_HANDLERS[command_name]


def budget_app_executor(command_line: str) -> str:
    parsed_command = parse_command_line(command_line)
    result = UNKNOWN_COMMAND_MSG

    if parsed_command is not None:
        command_name, command_args = parsed_command
        command_handler = get_command_handler(command_name)

        if command_handler is not None:
            result = command_handler(command_args)

    print(result)
    return result


def main() -> None:
    while True:
        command_line = input().strip()
        if command_line == EXIT_CMD:
            break
        budget_app_executor(command_line)


if __name__ == "__main__":
    main()
