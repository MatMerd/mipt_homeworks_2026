#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

DATE_LIST_LENGHT = 3
MONTHS_NUMBER = 12
FEBRUARY_NUMBER = 2
ALLOWED_SYMBOLS = "0123456789.-"
CATEGORY_PARTS_COUNT = 2
INCOME_QUERY_LENGTH = 3
COST_CATEGORIES_QUERY_LENGTH = 2
COST_QUERY_LENGTH = 4
STATS_QUERY_LENGTH = 2
AMOUNT_KEY = "amount"
DATE_KEY = "date"
CATEGORY_KEY = "category"

DAYS_IN_MONTH = (
    31, 28, 31, 30, 31, 30,
    31, 31, 30, 31, 30, 31
)

DATA_DATE = tuple[int, int, int]
RESULT_OF_CALC = tuple[float, float, dict[str, float]]
INCOM_EXPENSES_RESULT = tuple[float, float]
DETAILES_DATA = dict[str, float]
TRANSACTION_DATA = dict[str, Any]
DETAILES_CAT_DATA = dict[str, float]

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
    if year % 4 == 0 and year % 100 != 0:
        return True
    return year % 400 == 0


def get_days_in_month(month: int, year: int) -> int:
    if month == FEBRUARY_NUMBER and (is_leap_year(year)):
        return DAYS_IN_MONTH[month - 1] + 1
    return DAYS_IN_MONTH[month - 1]


def extract_date(maybe_dt: str) -> DATA_DATE | None:
    list_of_mabe_dt = maybe_dt.split("-")
    if len(list_of_mabe_dt) != DATE_LIST_LENGHT:
        return None

    if any(not date_fragment.isdigit() for date_fragment in list_of_mabe_dt):
        return None

    day = int(list_of_mabe_dt[0])
    month = int(list_of_mabe_dt[1])
    year = int(list_of_mabe_dt[2])

    if not (1 <= month <= MONTHS_NUMBER and year > 0):
        return None

    max_days = get_days_in_month(month, year)
    if not (1 <= day <= max_days):
        return None

    return day, month, year


def extract_amount(maybe_amount: str) -> float | None:
    maybe_amount = maybe_amount.replace(",", ".")

    if maybe_amount.startswith("-"):
        if maybe_amount.count("-") > 1:
            return None
        amount_str = maybe_amount[1:]
    else:
        amount_str = maybe_amount

    if amount_str.count(".") > 1:
        return None

    for symbol in amount_str:
        if not symbol.isdigit() and symbol != ".":
            return None

    amount = float(maybe_amount)

    if amount <= 0:
        return -1

    return amount


def validate_category(name_of_category: str) -> bool:
    category_parts = name_of_category.split("::")
    if len(category_parts) != CATEGORY_PARTS_COUNT:
        return False

    common_category, target_category = category_parts
    return common_category in EXPENSE_CATEGORIES and target_category in EXPENSE_CATEGORIES[common_category]


def get_target_category(category_name: str) -> str:
    return category_name.split("::", maxsplit=1)[1]


def save_transaction(transaction: dict[str, Any]) -> None:
    financial_transactions_storage.append(transaction)


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    date = extract_date(income_date)
    if date is None:
        return INCORRECT_DATE_MSG

    save_transaction({AMOUNT_KEY: amount, DATE_KEY: income_date})
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if not validate_category(category_name):
        return NOT_EXISTS_CATEGORY

    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    date = extract_date(income_date)
    if date is None:
        return INCORRECT_DATE_MSG

    save_transaction({CATEGORY_KEY: category_name, AMOUNT_KEY: amount, DATE_KEY: income_date})
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return "\n".join([
        f"{common_category}::{target_category}"
        for common_category, subcategories in EXPENSE_CATEGORIES.items()
        for target_category in subcategories
    ])

#тут типо скобочки, поэтому check это bool
#я проверяю что номер дня равер номеру другого дня
#и номер месяца равн номеру другого месяца
#CI ругался на сложность условия в if, поэтому пришлось разделить
def is_same_month(data1: DATA_DATE, data2: DATA_DATE) -> bool:
    first_check = (data1[1] == data2[1])
    second_check = (data1[2] == data2[2])
    return first_check and second_check

#проверяем именно сначала год, потом месяц, потом день
#потому что если я верну true на проверке дня это не значит, что
#дата реально была до другой, врдуг день рантше год позднее
#поэтому проверяем в обратном порядке
def is_date_before_or_equal(date1: DATA_DATE, date2: DATA_DATE) -> bool:
    for i in range(2, -1, -1):
        if date2[i] != date1[i]:
            return date1[i] < date2[i]
    return True


def calculate_month_stats(date: DATA_DATE) -> RESULT_OF_CALC:
    month_income = float(0)
    month_expenses = float(0)
    for transaction in financial_transactions_storage:
        if not transaction:
            continue

        if check_info_tr(transaction, date):
            continue

        income, expenses = process_transaction(transaction, date)
        month_income += income
        month_expenses += expenses

    return month_income, month_expenses, process_detailes_by_category(date)


def process_detailes_by_category(date: DATA_DATE) -> dict[str, float]:
    details_by_category: dict[str, float] = {}
    for transaction in financial_transactions_storage:
        if not transaction:
            continue

        if check_info_tr(transaction, date):
            continue

        details_by_category = process_transaction_detailes(transaction, date, details_by_category)

    return details_by_category


def process_income_transaction(amount: float, month_income: float) -> float:
    return month_income + amount


def process_detailes_transaction(
    amount: float,
    category: str,
    details_by_category: DETAILES_CAT_DATA
) -> DETAILES_CAT_DATA:
    target_category = get_target_category(category)
    details_by_category[target_category] = details_by_category.get(target_category, 0) + amount
    return details_by_category


def check_info_tr(
    transaction: TRANSACTION_DATA,
    date: DATA_DATE
) -> bool:
    tr_date = transaction.get(DATE_KEY)
    if tr_date is None:
        return True

    if not is_same_month(tr_date, date):
        return True

    return not bool(is_date_before_or_equal(date, tr_date))


def process_transaction(
    transaction: TRANSACTION_DATA,
    date: DATA_DATE,
) -> INCOM_EXPENSES_RESULT:
    month_income = float(0)
    month_expenses = float(0)

    if check_info_tr(transaction, date):
        return month_income, month_expenses

    amount = transaction.get(AMOUNT_KEY)
    if amount is None:
        return month_income, month_expenses

    category = transaction.get(CATEGORY_KEY)
    if category is None:
        month_income = process_income_transaction(amount, month_income)
    else:
        month_expenses += amount

    return month_income, month_expenses


def process_transaction_detailes(
    transaction: TRANSACTION_DATA,
    date: DATA_DATE,
    details_by_category: DETAILES_CAT_DATA
) -> dict[str, float]:
    if check_info_tr(transaction, date):
        return details_by_category

    amount = transaction.get(AMOUNT_KEY)
    if amount is None:
        return details_by_category

    category = transaction.get(CATEGORY_KEY)
    if category is not None:
        details_by_category = process_detailes_transaction(
            amount, category, details_by_category
        )
    return details_by_category


def calculate_total_capital() -> float:
    total_capital = 0

    for transaction in financial_transactions_storage:
        if not transaction:
            continue

        amount = transaction[AMOUNT_KEY]
        if CATEGORY_KEY in transaction:
            total_capital -= amount
        else:
            total_capital += amount

    return total_capital


def format_statistics(report_date: str, total: float, income: float, expenses: float, details: DETAILES_DATA) -> str:
    result_amount = abs(income - expenses)
    result_type = "loss" if income - expenses < 0 else "profit"

    statistics = [
        f"Your statistics as of {report_date}:",
        f"Total capital: {total:.2f} rubles",
        f"This month, the {result_type} amounted to {result_amount:.2f} rubles.",
        f"Income: {income:.2f} rubles",
        f"Expenses: {expenses:.2f} rubles",
        "",
        "Details (category: amount):",
    ]

    return sorting_categories(details, statistics)


def sorting_categories(details: DETAILES_DATA, statistics: list[str]) -> str:
    sorted_categories = sorted(details.items(), key=_category_key)
    for idx, (category_name, amount) in enumerate(sorted_categories, start=1):
        statistics.append(f"{idx}. {category_name}: {amount:.2f}")
    return "\n".join(statistics)


def _category_key(item: tuple[str, float]) -> str:
    return item[0].lower()


def stats_handler(report_date: str) -> str:
    date = extract_date(report_date)
    if date is None:
        return INCORRECT_DATE_MSG

    total_capital = calculate_total_capital()
    month_income, month_expenses, details_by_category = calculate_month_stats(date)

    return format_statistics(report_date, total_capital, month_income, month_expenses, details_by_category)


def output_handler(result: str) -> None:
    print(result)
    if result == NOT_EXISTS_CATEGORY:
        categories_info = cost_categories_handler()
        if categories_info:
            print(categories_info)


def handle_income_command(input_parts: list[str]) -> None:
    if len(input_parts) != INCOME_QUERY_LENGTH:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount = extract_amount(input_parts[1])
    if amount is None:
        print(UNKNOWN_COMMAND_MSG)
        return

    print(income_handler(amount, input_parts[2]))


def handle_cost(input_parts: list[str]) -> None:
    if len(input_parts) == COST_CATEGORIES_QUERY_LENGTH and input_parts[1] == "categories":
        print(cost_categories_handler())
        return

    if len(input_parts) != COST_QUERY_LENGTH:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount = extract_amount(input_parts[2])
    if amount is None:
        print(UNKNOWN_COMMAND_MSG)
        return

    output_handler(cost_handler(input_parts[1], amount, input_parts[3]))


def handle_stats_command(input_parts: list[str]) -> None:
    if len(input_parts) != STATS_QUERY_LENGTH:
        print(UNKNOWN_COMMAND_MSG)
        return

    print(stats_handler(input_parts[1]))


def dispatch_command(input_line: str) -> bool:
    input_parts = input_line.split()
    command_name = input_parts[0]

    if command_name == "income":
        handle_income_command(input_parts)
    elif command_name == "cost":
        handle_cost(input_parts)
    elif command_name == "stats":
        handle_stats_command(input_parts)
    else:
        print(UNKNOWN_COMMAND_MSG)

    return True


def main() -> None:
    false = True
    while false:
        input_line = input().strip()
        false = False if not input_line else dispatch_command(input_line)


if __name__ == "__main__":
    main()
