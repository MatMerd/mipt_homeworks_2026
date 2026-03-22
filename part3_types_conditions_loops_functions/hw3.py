#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"
DAY = 0
MONTH = 1
YEAR = 2
CAPITAL = 0
EARNINGS = 1
EXPENSES = 2
FEBRUARY = 2
LEAP_FEBRUARY = 29
NUMBER_OF_MONTHS = 12
NUMBER_OF_FIELDS = 3
INCOME_NUMBER_OF_ARGUMENTS = 3
COSTS_NUMBER_OF_ARGUMENTS = 4
STATS_NUMBER_OF_ARGUMENTS = 2
CONST_CATEGORY_NUMBER_OF_ARGUMENTS = 2
DEPTH_OF_CATEGORIES = 2
AMOUNT = "amount"
DATE = "date"
CATEGORY = "category"

DateTuple = tuple[int, int, int]


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

TABLE_ONE = {
    1: 31,
    2: 28,
    3: 31,
}

TABLE_TWO = {
    4: 30,
    5: 31,
    6: 30,
}

TABLE_THREE = {
    7: 31,
    8: 31,
    9: 30,
}

TABLE_FOUR = {
    10: 31,
    11: 30,
    12: 31,
}

TABLE = {
    **TABLE_ONE,
    **TABLE_TWO,
    **TABLE_THREE,
    **TABLE_FOUR,
}

financial_transactions_storage: list[dict[str, Any]] = []

leap_ct = [4, 100, 400]


def store_invalid_transaction(message: str) -> str:
    financial_transactions_storage.append({})
    return message


def categories_info() -> str:
    answer: list[str] = []
    for category, values in EXPENSE_CATEGORIES.items():
        answer.extend(f"{category}::{value}" for value in values)
    return "\n".join(answer)


def print_exp() -> None:
    print(categories_info())


def is_float(maybe_float: str) -> bool:
    if maybe_float.startswith(("+", "-")):
        maybe_float = maybe_float[1:]
    maybe_float = maybe_float.replace(",", ".", 1)
    maybe_float = maybe_float.replace(".", "", 1)
    return maybe_float.isdigit()


def is_leap_year(year: int) -> bool:
    by_four = year % leap_ct[0] == 0
    by_hundred = year % leap_ct[1] == 0
    by_four_hunder = year % leap_ct[2] == 0
    return (by_four and not by_hundred) or by_four_hunder


def number_of_days(month: int, year: int) -> int:
    if month == FEBRUARY and is_leap_year(year):
        return LEAP_FEBRUARY

    return TABLE[month]


def is_date_correct(day: int, month: int, year: int) -> bool:
    return 1 <= month <= NUMBER_OF_MONTHS and 1 <= day <= number_of_days(month, year)


def are_letters_correct(d_m_y: list[str]) -> bool:
    return all(x.lstrip("+-").isdigit() for x in d_m_y)


def extract_date(maybe_dt: str) -> DateTuple | None:
    d_m_y = list(maybe_dt.split("-"))

    if len(d_m_y) != NUMBER_OF_FIELDS or not are_letters_correct(d_m_y):
        return None

    day = int(d_m_y[DAY])
    month = int(d_m_y[MONTH])
    year = int(d_m_y[YEAR])

    if not is_date_correct(day, month, year):
        return None
    return (day, month, year)


def income_handler(amount: float, income_date: str) -> str:
    d_m_y = extract_date(income_date)

    if amount <= 0:
        return store_invalid_transaction(NONPOSITIVE_VALUE_MSG)

    if d_m_y is None:
        return store_invalid_transaction(INCORRECT_DATE_MSG)

    financial_transactions_storage.append({AMOUNT: amount, DATE: d_m_y})

    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    d_m_y = extract_date(income_date)

    if not correct_category(category_name):
        return store_invalid_transaction(NOT_EXISTS_CATEGORY)

    if amount <= 0:
        return store_invalid_transaction(NONPOSITIVE_VALUE_MSG)

    if d_m_y is None:
        return store_invalid_transaction(INCORRECT_DATE_MSG)

    financial_transactions_storage.append({CATEGORY: category_name, AMOUNT: amount, DATE: d_m_y})

    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return categories_info()


def output_stats_header(stats_date: str, capital: float, earnings: float, expenses: float) -> str:
    phrase = "loss"
    difference = expenses - earnings
    if earnings >= expenses:
        phrase = "profit"
        difference = earnings - expenses

    return f"Your statistics as of {stats_date}:\n\
Total capital: {capital:.2f} rubles\n\
This month, the {phrase} amounted to {difference:.2f} rubles\n\
Income: {earnings:.2f} rubles\n\
Expenses: {expenses:.2f} rubles\n\n"


def output_stats_detalisation(categ: dict[str, float]) -> str:
    detalisation = "Details (category: amount):"

    number = 1
    for rubric in sorted(categ):
        detalisation = f"{detalisation}\n{number}. {rubric}: {categ[rubric]:.2f}"
        number += 1
    return f"{detalisation}\n"


def is_earlier_eq(first: DateTuple, second: DateTuple) -> bool:
    if first[YEAR] != second[YEAR]:
        return first[YEAR] <= second[YEAR]
    if first[MONTH] != second[MONTH]:
        return first[MONTH] <= second[MONTH]
    return first[DAY] <= second[DAY]


def calc_capital(d_m_y: DateTuple) -> float:
    capital = float(0)
    for transac in financial_transactions_storage:
        current_date = transac.get(DATE)
        if current_date is None:
            continue
        if is_earlier_eq(current_date, d_m_y):
            if CATEGORY in transac:
                capital -= transac[AMOUNT]
            else:
                capital += transac[AMOUNT]
    return capital


def is_one_month(d_m_y: DateTuple, d_m_y_other: DateTuple) -> bool:
    same_year = d_m_y[YEAR] == d_m_y_other[YEAR]
    same_month = d_m_y[MONTH] == d_m_y_other[MONTH]
    return same_year and same_month


def accurate_categ(categ: dict[str, float], current_categ: str, amount: float) -> None:
    categ[current_categ] = categ.get(current_categ, float(0)) + amount


def is_current_month_transaction(transac: dict[str, Any], d_m_y: DateTuple) -> bool:
    current_date = transac.get(DATE)
    if current_date is None:
        return False
    return is_one_month(d_m_y, current_date) and is_earlier_eq(current_date, d_m_y)


def calc_income_cost(d_m_y: DateTuple) -> tuple[float, float, dict[str, float]]:
    categ: dict[str, float] = {}
    earnings = float(0)
    expenses = float(0)

    for transac in financial_transactions_storage:
        if is_current_month_transaction(transac, d_m_y):
            category_name = transac.get(CATEGORY)
            if category_name:
                expenses += transac[AMOUNT]
                accurate_categ(categ, category_name, transac[AMOUNT])
            else:
                earnings += transac[AMOUNT]
    return (earnings, expenses, categ)


def calc_finances(d_m_y: DateTuple) -> tuple[list[float], dict[str, float]]:
    capital = calc_capital(d_m_y)

    (earnings, expenses, categ) = calc_income_cost(d_m_y)

    return ([capital, earnings, expenses], categ)


def stats_handler(report_date: str) -> str:
    d_m_y = extract_date(report_date)

    if d_m_y is None:
        return INCORRECT_DATE_MSG
    (fin_header, fin_detal) = calc_finances(d_m_y)
    header = output_stats_header(report_date, *fin_header)
    detalisation = output_stats_detalisation(fin_detal)
    return f"{header}{detalisation}"


def valid_args_cost(elements: list[str]) -> bool:
    invalid_len = len(elements) != COSTS_NUMBER_OF_ARGUMENTS
    if invalid_len:
        print(UNKNOWN_COMMAND_MSG)
        return False

    empty_name = not elements[1].strip()
    invalid_value = not is_float(elements[2])
    if empty_name or invalid_value:
        print(UNKNOWN_COMMAND_MSG)
        return False
    return True


def valid_args_income(elements: list[str]) -> bool:
    if len(elements) != INCOME_NUMBER_OF_ARGUMENTS or not is_float(elements[1]):
        print(UNKNOWN_COMMAND_MSG)
        return False
    return True


def valid_args_stats(elements: list[str]) -> bool:
    if len(elements) != STATS_NUMBER_OF_ARGUMENTS:
        print(UNKNOWN_COMMAND_MSG)
        return False
    return True


def normalize_amount(raw_amount: str) -> float:
    return float(raw_amount.replace(",", ".", 1))


def handle_income(elements: list[str]) -> None:
    if not valid_args_income(elements):
        return
    amount = normalize_amount(elements[1])
    print(income_handler(amount, elements[2]))


def correct_category(category: str) -> bool:
    levels = list(category.split("::"))
    if len(levels) == DEPTH_OF_CATEGORIES:
        current_category = levels[0]
        if current_category not in EXPENSE_CATEGORIES:
            return False
        return levels[1] in EXPENSE_CATEGORIES[current_category]
    return False


def handle_cost(elements: list[str]) -> None:
    if len(elements) == CONST_CATEGORY_NUMBER_OF_ARGUMENTS and elements[1] == "categories":
        print(cost_categories_handler())
        return
    if not valid_args_cost(elements):
        return
    if not correct_category(elements[1]):
        print(NOT_EXISTS_CATEGORY)
        print_exp()
        return
    amount = normalize_amount(elements[2])
    print(cost_handler(elements[1], amount, elements[3]))


def handle_stats(elements: list[str]) -> None:
    if not valid_args_stats(elements):
        return
    print(stats_handler(elements[1]))


def process_command(elements: list[str]) -> None:
    if len(elements) == 0:
        print(UNKNOWN_COMMAND_MSG)
        return
    match elements[0]:
        case "income":
            handle_income(elements)
        case "cost":
            handle_cost(elements)
        case "stats":
            handle_stats(elements)
        case _:
            print(UNKNOWN_COMMAND_MSG)


def main() -> None:
    current_string = input()
    while current_string:
        elements = list(current_string.split())
        process_command(elements)
        current_string = input()


if __name__ == "__main__":
    main()
