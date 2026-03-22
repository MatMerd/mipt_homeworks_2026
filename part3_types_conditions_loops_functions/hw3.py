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


DateType = tuple[int, int, int]
TransactionType = dict[str, object]
CategoryTotalsType = dict[str, float]

financial_transactions_storage: list[TransactionType] = []

DATE_SEPARATOR = "-"
CATEGORY_SEPARATOR = "::"
DOT_SEPARATOR = "."
COMMA_SEPARATOR = ","
MINUS_SIGN = "-"

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
MAX_AMOUNT_PARTS = 2

ZERO = 0
ONE = 1

INCOME_COMMAND = "income"
COST_COMMAND = "cost"
STATS_COMMAND = "stats"
COST_CATEGORIES_COMMAND = "categories"

INCOME_COMMAND_PARTS_COUNT = 3
COST_CATEGORIES_COMMAND_PARTS_COUNT = 2
COST_COMMAND_PARTS_COUNT = 4
STATS_COMMAND_PARTS_COUNT = 2

TRANSACTION_TYPE_KEY = "type"
TRANSACTION_AMOUNT_KEY = "amount"
TRANSACTION_DATE_KEY = "date"
TRANSACTION_CATEGORY_KEY = "category"

CAPITAL_INDEX = 0
INCOME_INDEX = 1
EXPENSES_INDEX = 2

DAY_INDEX = 0
MONTH_INDEX = 1
YEAR_INDEX = 2
TARGET_CATEGORY_INDEX = 1

DAYS_IN_MONTH = (
    31,
    28,
    31,
    30,
    31,
    30,
    31,
    31,
    30,
    31,
    30,
    31,
)


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


def has_valid_date_parts_format(date_parts: list[str]) -> bool:
    if len(date_parts) != DATE_PARTS_COUNT:
        return False

    lengths = (
        DAY_PART_LENGTH,
        MONTH_PART_LENGTH,
        YEAR_PART_LENGTH,
    )
    return all(
        part.isdigit() and len(part) == part_length
        for part, part_length in zip(date_parts, lengths, strict=True)
    )


def get_month_day_limit(month: int, year: int) -> int:
    month_limit = DAYS_IN_MONTH[month - MIN_MONTH]
    if month == FEBRUARY and is_leap_year(year):
        return LEAP_DAY_COUNT_IN_FEBRUARY
    return month_limit


def has_valid_date_values(date_value: DateType) -> bool:
    day, month, year = date_value
    if month < MIN_MONTH or month > MAX_MONTH:
        return False
    return MIN_DAY <= day <= get_month_day_limit(month, year)


def extract_date(maybe_dt: str) -> DateType | None:
    date_parts = maybe_dt.split(DATE_SEPARATOR)
    if has_valid_date_parts_format(date_parts):
        return extract_valid_date(maybe_dt)
    return None


def extract_valid_date(maybe_dt: str) -> DateType | None:
    day_month_year = maybe_dt.split(DATE_SEPARATOR)
    parsed_date = (
        int(day_month_year[DAY_INDEX]),
        int(day_month_year[MONTH_INDEX]),
        int(day_month_year[YEAR_INDEX]),
    )
    if not has_valid_date_values(parsed_date):
        return None

    return parsed_date


def extract_category_parts(category_name: str) -> tuple[str, str] | None:
    category_parts = category_name.split(CATEGORY_SEPARATOR)
    if len(category_parts) != CATEGORY_PARTS_COUNT:
        return None
    return category_parts[0], category_parts[TARGET_CATEGORY_INDEX]


def is_valid_category_name(category_name: str) -> bool:
    category_parts = extract_category_parts(category_name)
    if category_parts is None:
        return False

    common_category, target_category = category_parts
    return (
        common_category in EXPENSE_CATEGORIES
        and target_category in EXPENSE_CATEGORIES[common_category]
    )


def append_empty_transaction() -> None:
    financial_transactions_storage.append({})


def make_income_transaction(amount: float, income_date: DateType) -> TransactionType:
    return {
        TRANSACTION_TYPE_KEY: INCOME_COMMAND,
        TRANSACTION_AMOUNT_KEY: amount,
        TRANSACTION_DATE_KEY: income_date,
    }


def make_cost_transaction(
    category_name: str,
    amount: float,
    cost_date: DateType,
) -> TransactionType:
    return {
        TRANSACTION_TYPE_KEY: COST_COMMAND,
        TRANSACTION_CATEGORY_KEY: category_name,
        TRANSACTION_AMOUNT_KEY: amount,
        TRANSACTION_DATE_KEY: cost_date,
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


def extract_transaction_date(transaction: TransactionType) -> DateType | None:
    raw_date = transaction.get(TRANSACTION_DATE_KEY)
    if not isinstance(raw_date, tuple) or len(raw_date) != DATE_PARTS_COUNT:
        return None

    if not all(isinstance(value, int) for value in raw_date):
        return None

    day, month, year = raw_date
    return day, month, year


def is_not_later_date(date1: DateType, date2: DateType) -> bool:
    return (date1[YEAR_INDEX], date1[MONTH_INDEX], date1[DAY_INDEX]) <= (
        date2[YEAR_INDEX],
        date2[MONTH_INDEX],
        date2[DAY_INDEX],
    )


def is_same_month(date1: DateType, date2: DateType) -> bool:
    return get_month_year(date1) == get_month_year(date2)


def get_month_year(date_value: DateType) -> tuple[int, int]:
    return date_value[MONTH_INDEX], date_value[YEAR_INDEX]


def extract_transaction_amount(transaction: TransactionType) -> float | None:
    raw_amount = transaction.get(TRANSACTION_AMOUNT_KEY)
    if not isinstance(raw_amount, int | float):
        return None
    return float(raw_amount)


def extract_target_category_name(category_name: str) -> str:
    category_parts = extract_category_parts(category_name)
    if category_parts is None:
        return category_name
    return category_parts[TARGET_CATEGORY_INDEX]


def add_cost_to_categories(
    transaction: TransactionType,
    amount: float,
    expenses_by_categories: CategoryTotalsType,
) -> None:
    raw_category = transaction.get(TRANSACTION_CATEGORY_KEY)
    if not isinstance(raw_category, str):
        return
    target_category = extract_target_category_name(raw_category)
    previous_amount = expenses_by_categories.get(target_category, float(ZERO))
    expenses_by_categories[target_category] = previous_amount + amount


def update_totals(
    transaction: TransactionType,
    report_date: DateType,
    totals: list[float],
    expenses_by_categories: CategoryTotalsType,
) -> None:
    transaction_date = extract_transaction_date(transaction)
    if transaction_date is None or not is_not_later_date(transaction_date, report_date):
        return

    amount = extract_transaction_amount(transaction)
    if amount is None:
        return

    is_cost = transaction.get(TRANSACTION_TYPE_KEY) == COST_COMMAND
    if is_cost:
        totals[CAPITAL_INDEX] -= amount
    else:
        totals[CAPITAL_INDEX] += amount

    if not is_same_month(transaction_date, report_date):
        return

    if is_cost:
        totals[EXPENSES_INDEX] += amount
        add_cost_to_categories(transaction, amount, expenses_by_categories)
    else:
        totals[INCOME_INDEX] += amount


def collect_statistics(report_date: DateType) -> tuple[list[float], CategoryTotalsType]:
    totals = [float(ZERO), float(ZERO), float(ZERO)]
    expenses_by_categories: CategoryTotalsType = {}
    for transaction in financial_transactions_storage:
        if transaction:
            update_totals(transaction, report_date, totals, expenses_by_categories)
    return totals, expenses_by_categories


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

    totals, expenses_by_categories = collect_statistics(parsed_report_date)

    return build_stats_summary(
        report_date=report_date,
        total_capital=totals[CAPITAL_INDEX],
        month_income=totals[INCOME_INDEX],
        month_expenses=totals[EXPENSES_INDEX],
        expenses_by_categories=expenses_by_categories,
    )


def has_valid_amount_format(raw_amount: str) -> bool:
    if not raw_amount:
        return False

    amount_without_sign = raw_amount.removeprefix(MINUS_SIGN)
    if not amount_without_sign:
        return False

    normalized_amount = amount_without_sign.replace(COMMA_SEPARATOR, DOT_SEPARATOR)
    if normalized_amount.count(DOT_SEPARATOR) > ONE:
        return False

    amount_parts = normalized_amount.split(DOT_SEPARATOR)
    if len(amount_parts) > MAX_AMOUNT_PARTS:
        return False

    return all(amount_parts) and all(part.isdigit() for part in amount_parts)


def parse_amount(raw_amount: str) -> float | None:
    if not has_valid_amount_format(raw_amount):
        return None
    return float(raw_amount.replace(COMMA_SEPARATOR, DOT_SEPARATOR))


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
