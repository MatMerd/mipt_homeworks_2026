#!/usr/bin/env python

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
    "Other": ("SomeCategory", "SomeOtherCategory"),
}


financial_transactions_storage: list[dict[str, object]] = []

DATE_SEPARATOR = "-"
CATEGORY_SEPARATOR = "::"

MIN_MONTH = 1
MAX_MONTH = 12
MIN_DAY = 1
FEBRUARY = 2
LEAP_DAY_COUNT_IN_FEBRUARY = 29

DATE_PARTS_COUNT = 3
DAY_PART_LENGTH = 2
MONTH_PART_LENGTH = 2
YEAR_PART_LENGTH = 4
CATEGORY_PARTS_COUNT = 2

INCOME_COMMAND = "income"
COST_COMMAND = "cost"
STATS_COMMAND = "stats"
COST_CATEGORIES_COMMAND = "categories"

INCOME_COMMAND_PARTS_COUNT = 3
COST_CATEGORIES_COMMAND_PARTS_COUNT = 2
COST_COMMAND_PARTS_COUNT = 4
STATS_COMMAND_PARTS_COUNT = 2

DAYS_IN_MONTH = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


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


def has_valid_date_parts_format(day_part: str, month_part: str, year_part: str) -> bool:
    return (
        day_part.isdigit()
        and month_part.isdigit()
        and year_part.isdigit()
        and len(day_part) == DAY_PART_LENGTH
        and len(month_part) == MONTH_PART_LENGTH
        and len(year_part) == YEAR_PART_LENGTH
    )


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    day_month_year = maybe_dt.split(DATE_SEPARATOR)
    if len(day_month_year) != DATE_PARTS_COUNT:
        return None

    day_part, month_part, year_part = day_month_year
    if not has_valid_date_parts_format(day_part, month_part, year_part):
        return None

    day = int(day_part)
    month = int(month_part)
    year = int(year_part)

    if month < MIN_MONTH or month > MAX_MONTH:
        return None

    max_day = DAYS_IN_MONTH[month - 1]
    if month == FEBRUARY and is_leap_year(year):
        max_day = LEAP_DAY_COUNT_IN_FEBRUARY

    if day < MIN_DAY or day > max_day:
        return None

    return day, month, year


def is_valid_category_name(category_name: str) -> bool:
    common_and_target = category_name.split(CATEGORY_SEPARATOR)
    if len(common_and_target) != CATEGORY_PARTS_COUNT:
        return False

    common_category, target_category = common_and_target
    return (
        common_category in EXPENSE_CATEGORIES
        and target_category in EXPENSE_CATEGORIES[common_category]
    )


def append_empty_transaction() -> None:
    financial_transactions_storage.append({})


def make_income_transaction(amount: float, income_date: tuple[int, int, int]) -> dict[str, object]:
    return {
        "type": INCOME_COMMAND,
        "amount": amount,
        "date": income_date,
    }


def make_cost_transaction(
    category_name: str,
    amount: float,
    cost_date: tuple[int, int, int],
) -> dict[str, object]:
    return {
        "type": COST_COMMAND,
        "category": category_name,
        "amount": amount,
        "date": cost_date,
    }


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        append_empty_transaction()
        return NONPOSITIVE_VALUE_MSG

    parsed_income_date = extract_date(income_date)
    if parsed_income_date is None:
        append_empty_transaction()
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append(make_income_transaction(amount, parsed_income_date))
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if amount <= 0:
        append_empty_transaction()
        return NONPOSITIVE_VALUE_MSG

    if not is_valid_category_name(category_name):
        append_empty_transaction()
        return NOT_EXISTS_CATEGORY

    parsed_cost_date = extract_date(income_date)
    if parsed_cost_date is None:
        append_empty_transaction()
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append(make_cost_transaction(category_name, amount, parsed_cost_date))
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return "\n".join(
        f"{common_category}{CATEGORY_SEPARATOR}{target_category}"
        for common_category, target_categories in EXPENSE_CATEGORIES.items()
        for target_category in target_categories
    )


def is_valid_storage_date(value: object) -> bool:
    if not isinstance(value, tuple) or len(value) != DATE_PARTS_COUNT:
        return False
    day, month, year = value
    return isinstance(day, int) and isinstance(month, int) and isinstance(year, int)


def is_not_later_date(date1: tuple[int, int, int], date2: tuple[int, int, int]) -> bool:
    day1, month1, year1 = date1
    day2, month2, year2 = date2
    return (year1, month1, day1) <= (year2, month2, day2)


def is_same_month(date1: tuple[int, int, int], date2: tuple[int, int, int]) -> bool:
    return date1[1] == date2[1] and date1[2] == date2[2]


def get_target_category_name(category_name: str) -> str:
    if CATEGORY_SEPARATOR not in category_name:
        return category_name
    return category_name.split(CATEGORY_SEPARATOR)[1]


def extract_storage_transaction_date(transaction: dict[str, object]) -> tuple[int, int, int] | None:
    raw_date = transaction.get("date")
    if not is_valid_storage_date(raw_date):
        return None
    return raw_date


def extract_storage_transaction_amount(transaction: dict[str, object]) -> float | None:
    raw_amount = transaction.get("amount")
    if not isinstance(raw_amount, int | float):
        return None
    return float(raw_amount)


def calculate_month_data_with_transaction(
    transaction: dict[str, object],
    amount: float,
    current_month_income: float,
    current_month_expenses: float,
    expenses_by_categories: dict[str, float],
) -> tuple[float, float]:
    is_cost_transaction = transaction.get("type") == COST_COMMAND
    if is_cost_transaction:
        current_month_expenses += amount
        raw_category = transaction.get("category")
        if isinstance(raw_category, str):
            target_category = get_target_category_name(raw_category)
            stored_amount = expenses_by_categories.get(target_category, 0.0)
            expenses_by_categories[target_category] = stored_amount + amount
    else:
        current_month_income += amount

    return current_month_income, current_month_expenses


def build_stats_summary(
    report_date: str,
    total_capital: float,
    month_income: float,
    month_expenses: float,
    expenses_by_categories: dict[str, float],
) -> str:
    month_balance = month_income - month_expenses
    month_state = "profit" if month_balance >= 0 else "loss"

    report_lines = [
        f"Your statistics as of {report_date}:",
        f"Total capital: {total_capital:.2f} rubles",
        f"This month, the {month_state} amounted to {abs(month_balance):.2f} rubles.",
        f"Income: {month_income:.2f} rubles",
        f"Expenses: {month_expenses:.2f} rubles",
        "",
        "Details (category: amount):",
    ]

    for index, category_name in enumerate(sorted(expenses_by_categories), start=1):
        report_lines.append(f"{index}. {category_name}: {expenses_by_categories[category_name]:.2f}")

    return "\n".join(report_lines)


def stats_handler(report_date: str) -> str:
    parsed_report_date = extract_date(report_date)
    if parsed_report_date is None:
        return INCORRECT_DATE_MSG

    total_capital = 0.0
    month_income = 0.0
    month_expenses = 0.0
    expenses_by_categories: dict[str, float] = {}

    for transaction in financial_transactions_storage:
        if not transaction:
            continue

        transaction_date = extract_storage_transaction_date(transaction)
        if transaction_date is None:
            continue

        if not is_not_later_date(transaction_date, parsed_report_date):
            continue

        amount = extract_storage_transaction_amount(transaction)
        if amount is None:
            continue

        is_cost_transaction = transaction.get("type") == COST_COMMAND
        capital_delta = -amount if is_cost_transaction else amount
        total_capital += capital_delta

        if not is_same_month(transaction_date, parsed_report_date):
            continue

        month_income, month_expenses = calculate_month_data_with_transaction(
            transaction=transaction,
            amount=amount,
            current_month_income=month_income,
            current_month_expenses=month_expenses,
            expenses_by_categories=expenses_by_categories,
        )

    return build_stats_summary(
        report_date=report_date,
        total_capital=total_capital,
        month_income=month_income,
        month_expenses=month_expenses,
        expenses_by_categories=expenses_by_categories,
    )


def has_valid_amount_format(raw_amount: str) -> bool:
    if not raw_amount:
        return False

    amount_without_sign = raw_amount.removeprefix("-")
    if not amount_without_sign:
        return False

    if amount_without_sign.count(".") + amount_without_sign.count(",") > 1:
        return False

    if "." in amount_without_sign and "," in amount_without_sign:
        return False

    if "." in amount_without_sign:
        integer_part, float_part = amount_without_sign.split(".")
    elif "," in amount_without_sign:
        integer_part, float_part = amount_without_sign.split(",")
    else:
        return amount_without_sign.isdigit()

    return bool(integer_part) and bool(float_part) and integer_part.isdigit() and float_part.isdigit()


def parse_amount(raw_amount: str) -> float | None:
    if not has_valid_amount_format(raw_amount):
        return None
    return float(raw_amount.replace(",", "."))


def process_income_command(command_parts: list[str]) -> str:
    if len(command_parts) != INCOME_COMMAND_PARTS_COUNT:
        return UNKNOWN_COMMAND_MSG

    amount = parse_amount(command_parts[1])
    if amount is None:
        return NONPOSITIVE_VALUE_MSG

    return income_handler(amount, command_parts[2])


def process_cost_command(command_parts: list[str]) -> str:
    if (
        len(command_parts) == COST_CATEGORIES_COMMAND_PARTS_COUNT
        and command_parts[1] == COST_CATEGORIES_COMMAND
    ):
        return cost_categories_handler()

    if len(command_parts) != COST_COMMAND_PARTS_COUNT:
        return UNKNOWN_COMMAND_MSG

    amount = parse_amount(command_parts[2])
    if amount is None:
        return NONPOSITIVE_VALUE_MSG

    return cost_handler(command_parts[1], amount, command_parts[3])


def process_stats_command(command_parts: list[str]) -> str:
    if len(command_parts) != STATS_COMMAND_PARTS_COUNT:
        return UNKNOWN_COMMAND_MSG
    return stats_handler(command_parts[1])


def process_command(raw_command: str) -> str:
    command_parts = raw_command.strip().split()
    if not command_parts:
        return UNKNOWN_COMMAND_MSG

    command_name = command_parts[0]
    if command_name == INCOME_COMMAND:
        return process_income_command(command_parts)
    if command_name == COST_COMMAND:
        return process_cost_command(command_parts)
    if command_name == STATS_COMMAND:
        return process_stats_command(command_parts)
    return UNKNOWN_COMMAND_MSG


def main() -> None:
    while True:
        user_input = input().strip()
        if user_input == "":
            break
        print(process_command(user_input))


if __name__ == "__main__":
    main()
