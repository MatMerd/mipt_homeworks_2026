#!/usr/bin/env python
from typing import Any

DataTuple = tuple[int, int, int]

financial_transactions_storage: list[dict[str, Any]] = []

DATE_KEY = "date"
CATEGORY_KEY = "category"
AMOUNT_KEY = "amount"
LEN_DATE_LIST = 3
MONTHS_THIRTY_DAYS = (4, 6, 9, 11)
FEBRUARY = 2
MIN_MONTH = 1
MAX_MONTH = 12
MIN_DAY = 1
MAX_DAY_IN_THIRTY_DAYS_MONTH = 30
MAX_DAY_IN_THIRTY_ONE_DAY_MONTH = 31
MAX_DAY_FEB_LEAP = 29
MAX_DAY_FEB_NORMAL = 28
DATE_LENGTH = 10
INCOME_ARGS = 3
COST_ARGS_TO_OPERATE = 4
COST_ARGS_TO_GET_CATEGORIES = 2
STATS_ARGS = 2
LEN_CATEGORY_PATH = 2
STATS_PRINT = """Your statistics as of {}:
Total capital: {} rubles
This month, {} amounted to {} rubles.
Income: {} rubles
Expenses: {} rubles

Details (category: amount):"""

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"
NOT_EXISTS_CATEGORY = "Category not exists!"

EXPENSE_CATEGORIES: dict[str, tuple[str, ...]] = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": (),
}


def income(amount: float, date: str) -> str:
    if amount > 0:
        tuple_date = extract_data(date)
        if tuple_date is not None:
            return income_handler(amount, date)
        return INCORRECT_DATE_MSG
    return NONPOSITIVE_VALUE_MSG


def cost_operation(category_name: str, amount: float, date: str) -> str:
    if categories_validate(category_name):
        category_path = category_name.split("::")
        if amount > 0:
            tuple_date = extract_data(date)
            if tuple_date is not None:
                return cost_handler(category_path[1], amount, date)
            return INCORRECT_DATE_MSG
        return NONPOSITIVE_VALUE_MSG
    return NOT_EXISTS_CATEGORY


def cost_get_categories(categories: str) -> str:
    if categories == "categories":
        return cost_categories_handler()
    return UNKNOWN_COMMAND_MSG


def stats(date: str) -> str:
    tuple_date = extract_data(date)
    if tuple_date is not None:
        month_profit = print_month_profit(tuple_date)
        if float(month_profit) > 0:
            result = STATS_PRINT.format(date,
                                        print_capital(tuple_date),
                                        "the profit",
                                        month_profit,
                                        print_month_income(tuple_date),
                                        print_month_expense(tuple_date)
                                        )
            lines = [result]
            lines.extend(print_categories(tuple_date))
            return "\n".join(lines)
        result = STATS_PRINT.format(date,
                                    print_capital(tuple_date),
                                    "the loss",
                                    month_profit,
                                    print_month_income(tuple_date),
                                    print_month_expense(tuple_date)
                                    )
        lines = [result]
        lines.extend(print_categories(tuple_date))
        return "\n".join(lines)
    return INCORRECT_DATE_MSG


def print_categories(tuple_date: DataTuple) -> list[str]:
    categories = count_categories(tuple_date)
    categories_print: list[str] = []
    if categories:
        idx = 1
        for cat, amount in categories.items():
            categories_print.append(f"\n{idx}. {cat}: {amount:.0f}")
    return categories_print


def print_capital(tuple_date: DataTuple) -> str:
    capital = count_capital(tuple_date)
    return f"{capital:.2f}"


def print_month_expense(tuple_date: DataTuple) -> str:
    month_expense = count_monthly_expense(tuple_date)
    return f"{month_expense:.2f}"


def print_month_income(tuple_date: DataTuple) -> str:
    month_income = count_monthly_income(tuple_date)
    return f"{month_income:.2f}"


def print_month_profit(tuple_date: DataTuple) -> str:
    month_profit = count_monthly_income(tuple_date) - count_monthly_expense(tuple_date)
    return f"{month_profit:.2f}"


def count_capital(tuple_date: DataTuple) -> float:
    total_income = float(0)
    for transaction in financial_transactions_storage:
        dt = get_tuple_date(transaction[DATE_KEY])
        if compare_date(tuple_date, dt):
            if CATEGORY_KEY in transaction:
                total_income -= transaction[AMOUNT_KEY]
            else:
                total_income += transaction[AMOUNT_KEY]
    return total_income


def count_monthly_income(tuple_date: DataTuple) -> float:
    monthly_income = float(0)
    for transaction in financial_transactions_storage:
        dt = get_tuple_date(transaction[DATE_KEY])
        if CATEGORY_KEY not in transaction and compare_date(tuple_date, dt) and is_same_month(tuple_date, dt):
            monthly_income += transaction[AMOUNT_KEY]
    return monthly_income


def count_monthly_expense(tuple_date: DataTuple) -> float:
    monthly_expense = float(0)
    for transaction in financial_transactions_storage:
        dt = get_tuple_date(transaction[DATE_KEY])
        if CATEGORY_KEY in transaction and compare_date(tuple_date, dt) and is_same_month(tuple_date, dt):
            monthly_expense += transaction[AMOUNT_KEY]
    return monthly_expense


def count_categories(tuple_date: DataTuple) -> dict[str, float]:
    categories: dict[str, float] = {}
    for transaction in financial_transactions_storage:
        if CATEGORY_KEY in transaction:
            dt = get_tuple_date(transaction[DATE_KEY])
            if compare_date(tuple_date, dt) and is_same_month(tuple_date, dt):
                cat = transaction.get(DATE_KEY, "")
                amount = transaction[AMOUNT_KEY]
                categories[cat] = categories.get(cat, float(0)) + amount
    return dict(sorted(categories.items()))


def is_same_month(date1: DataTuple, date2: DataTuple) -> bool:
    return date1[1:] == date2[1:]


def compare_date(first: DataTuple, second: DataTuple) -> bool:
    if first[2] != second[2]:
        return first[2] > second[2]
    if first[1] != second[1]:
        return first[1] > second[1]
    return first[0] >= second[0]


def date_validation(day: int, month: int, year: int) -> bool:
    if not (MIN_MONTH <= month <= MAX_MONTH):
        return False
    if day < MIN_DAY:
        return False
    if month in MONTHS_THIRTY_DAYS:
        return day <= MAX_DAY_IN_THIRTY_DAYS_MONTH
    if month == FEBRUARY:
        max_day = MAX_DAY_FEB_LEAP if is_leap_year(year) else MAX_DAY_FEB_NORMAL
        return day <= max_day
    return day <= MAX_DAY_IN_THIRTY_ONE_DAY_MONTH


def categories_validate(category_name: str) -> bool:
    category_path = category_name.split("::")
    return (len(category_path) == LEN_CATEGORY_PATH and
            category_path[0] in EXPENSE_CATEGORIES and
            category_path[1] in EXPENSE_CATEGORIES[category_path[0]])


def main() -> None:
    while True:
        input_line = input().replace(",", ".").split()
        if not input_line:
            return
        command = input_line[0]
        match command:
            case "income":
                print(process_income(input_line))
            case "cost":
                print(process_cost(input_line))
            case "stats":
                print(process_stats(input_line))
            case _:
                print(UNKNOWN_COMMAND_MSG)


def process_income(input_line: list[str]) -> str:
    if len(input_line) == INCOME_ARGS:
        return income(float(input_line[1]), input_line[2])
    return UNKNOWN_COMMAND_MSG


def process_cost(input_line: list[str]) -> Any:
    if len(input_line) == COST_ARGS_TO_OPERATE:
        return cost_operation(input_line[1], float(input_line[2]), input_line[3])
    if len(input_line) == COST_ARGS_TO_GET_CATEGORIES:
        return cost_get_categories(input_line[1])
    return UNKNOWN_COMMAND_MSG


def process_stats(input_line: list[str]) -> str:
    if len(input_line) == STATS_ARGS:
        return stats(input_line[1])
    return UNKNOWN_COMMAND_MSG


def is_leap_year(year: int) -> bool:
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0


def income_handler(amount: float, income_date: str) -> str:
    financial_transactions_storage.append({AMOUNT_KEY: amount, DATE_KEY: income_date})
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    financial_transactions_storage.append({CATEGORY_KEY: category_name, AMOUNT_KEY: amount, DATE_KEY: income_date})
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    lines: list[str] = []
    for main_cat, sub_cats in EXPENSE_CATEGORIES.items():
        if sub_cats:
            lines.extend(f"{main_cat}::{sub_cat}" for sub_cat in sub_cats)
    return "\n".join(lines)


def extract_data(maybe_dt: str) -> DataTuple | None:
    if len(maybe_dt) == DATE_LENGTH and maybe_dt.count("-"):
        tuple_date = get_tuple_date(maybe_dt)
        if date_validation(tuple_date[0], tuple_date[1], tuple_date[2]):
            return tuple_date
    return None


def get_tuple_date(date: str) -> DataTuple:
    day, month, year = map(int, date.split("-"))
    return (day, month, year)


if __name__ == "__main__":
    main()
