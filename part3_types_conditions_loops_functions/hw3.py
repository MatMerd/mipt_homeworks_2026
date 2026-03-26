#!/usr/bin/env python
import string
from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"
DIGITS = string.digits
LETTERS = string.ascii_letters
INCOME_REQUEST = "income"
COST_REQUEST = "cost"
STATS_REQUEST = "stats"
REQUEST_TYPE = "request_type"
AMOUNT = "amount"
DATE = "date"
CATEGORY = "category"
TIRE = "-"
DATE_SIZE = 10
FEBRUARY = 2
FEBRUARY_LAST = 29
MONTHS_TOTAL = 12
TWO = 2
THREE = 3

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

REQUEST_TYPES = [
    INCOME_REQUEST,
    COST_REQUEST,
    STATS_REQUEST
]

MONTHS_DAYS = {
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
    12: 31
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


def number_parser(num: str) -> float | None:
    bad1 = num == ""
    bad2 = num.count(".") + num.count(",") > 1
    bad3 = num[0] == TIRE
    bad4 = num[0] == "." or num[0] == ","
    if bad1 or bad2 or bad3 or bad4:
        return None
    for elem in num:
        bad5 = elem not in DIGITS
        bad6 = elem in {".", ","}
        if bad5 or bad6:
            return None
    if num[-1] == "." or num[-1] == ",":
        return None
    num = num.replace(",", ".")
    return float(num)


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    bad1 = len(maybe_dt) != DATE_SIZE
    bad2 = maybe_dt[2] != TIRE or maybe_dt[5] != TIRE
    if bad1 or bad2:
        return None
    for i in (0, 1, 3, 4, 6, 7, 8, 9):
        if maybe_dt[i] not in DIGITS:
            return None
    day = int(maybe_dt[:2])
    month = int(maybe_dt[3:5])
    year = int(maybe_dt[6:])
    date = (day, month, year)
    is_february_leap = is_leap_year(date[2]) and date[1] == FEBRUARY
    if is_february_leap and date[0] <= FEBRUARY_LAST:
        return date
    bad3 = date[1] < 1
    bad4 = date[1] > MONTHS_TOTAL
    bad5 = date[0] > MONTHS_DAYS[date[1]]
    if bad3 or bad4 or bad5:
        return None
    return date


def to_str_date(date: list[int, int, int]) -> str:
    for i in range(2):
        parts = []
        if len(str(date[i])) == 1:
            parts.append("0")
        parts.append(date[i])
        parts.append(TIRE)
    parts.append(date[2])
    return "".join(parts)


def less_or_equal(date1: str, date2: str) -> bool:
    for i in range(0, 3, -1):
        if date1[i] < date2[i]:
            return True
        if date1[i] > date2[i]:
            return False
    return True


def category_parser(category: str) -> list[str] | None:
    if category.count(":") != TWO or category.count("::") != 1:
        return None
    for elem in category:
        if elem not in LETTERS and elem != ":":
            return None
    returner = category.split("::")
    bad1 = returner[0] not in EXPENSE_CATEGORIES
    bad2 = returner[1] not in EXPENSE_CATEGORIES[returner[0]]
    if bad1 or bad2:
        return None
    return returner


def income_request_parser(request_chopped: list[str]) -> dict | str:
    if len(request_chopped) != THREE:
        return UNKNOWN_COMMAND_MSG
    amount = number_parser(request_chopped[1])
    if amount is None:
        return NONPOSITIVE_VALUE_MSG
    date = extract_date(request_chopped[2])
    if date is None:
        return INCORRECT_DATE_MSG
    return {REQUEST_TYPE: INCOME_REQUEST,
            AMOUNT: amount,
            DATE: date}


def cost_request_parser(request_chopped: list[str]) -> dict | str:
    if len(request_chopped) not in [2, 4]:
        return UNKNOWN_COMMAND_MSG
    if len(request_chopped) == TWO and request_chopped[1] == "categories":
        return {REQUEST_TYPE: "cost_categories"}
    category = category_parser(request_chopped[1])
    amount = number_parser(request_chopped[2])
    date = extract_date(request_chopped[3])
    error = None
    if category is None:
        error = NOT_EXISTS_CATEGORY
    elif amount is None:
        error = NONPOSITIVE_VALUE_MSG
    elif date is None:
        error = INCORRECT_DATE_MSG
    if error is not None:
        return error
    return {REQUEST_TYPE: COST_REQUEST,
            "common_category": category[0],
            "target_category": category[1],
            AMOUNT: amount,
            DATE: date}


def stats_request_parser(request_chopped: list[str]) -> dict | str:
    if len(request_chopped) != TWO:
        return UNKNOWN_COMMAND_MSG
    date = extract_date(request_chopped[1])
    if date is None:
        return INCORRECT_DATE_MSG
    return {REQUEST_TYPE: STATS_REQUEST,
            DATE: date}


def request_parser(request: str) -> dict | str:
    request_chopped = request.split()
    if request_chopped[0] not in REQUEST_TYPES:
        return UNKNOWN_COMMAND_MSG
    if request_chopped[0] == INCOME_REQUEST:
        return income_request_parser(request_chopped)
    if request_chopped[0] == COST_REQUEST:
        return cost_request_parser(request_chopped)
    if request_chopped[0] == STATS_REQUEST:
        return stats_request_parser(request_chopped)
    return ""


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG
    if extract_date(income_date) is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG
    financial_transactions_storage.append({REQUEST_TYPE: INCOME_REQUEST,
                                           AMOUNT: amount,
                                           DATE: extract_date(income_date)})
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if category_parser(category_name) is None:
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY
    common_category, target_category = category_parser(category_name)
    bad1 = common_category not in EXPENSE_CATEGORIES
    bad2 = target_category not in EXPENSE_CATEGORIES[common_category]
    if bad1 or bad2:
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG
    if extract_date(income_date) is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG
    financial_transactions_storage.append({REQUEST_TYPE: COST_REQUEST,
                                           CATEGORY: category_name,
                                           AMOUNT: amount,
                                           DATE: extract_date(income_date)})
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    lines = []
    for key, values in EXPENSE_CATEGORIES.items():
        lines.extend(f"{key}::{value}" for value in values)
    return "\n".join(lines)


def stats_handler(report_date: str) -> str:
    income = 0
    expenses = 0
    detailed_expenses = {}
    for elem in financial_transactions_storage:
        if less_or_equal(elem[DATE], report_date):
            if elem[REQUEST_TYPE] == INCOME_REQUEST:
                income += elem[AMOUNT]
            else:
                expenses += elem[AMOUNT]
                category = elem[CATEGORY]
                detailed_expenses[category] += detailed_expenses.get(category, 0) + elem[AMOUNT]\

    total_capital = income - expenses

    parts = [f"Your statistics as of {report_date}:\n",
             f"Total capital: {total_capital} rubles\n"]
    if total_capital > 0:
        parts.append(f"This month, the profit amounted to {total_capital} rubles.\n")
    else:
        parts.append(f"This month, the loss amounted to {total_capital} rubles.\n")
    parts.append(f"Income: {income} rubles\n"
                 f"Expenses: {expenses} rubles\n\n"
                 f"Details (category: amount):\n")
    counter = 1
    for element in detailed_expenses.items():
        parts.append(f"{counter}. {element}: {detailed_expenses[element]}\n")
        counter += 1
    return "".join(parts)


def request_handler(request: dict | str) -> None:
    if request[REQUEST_TYPE] == INCOME_REQUEST:
        print(income_handler(request[AMOUNT],
                             to_str_date(request[DATE])))
    elif request[REQUEST_TYPE] == "cost_categories":
        print(cost_categories_handler())
    elif request[REQUEST_TYPE] == COST_REQUEST:
        print(cost_handler(f"{request["common_category"]}::{request["target_category"]}",
                           request[AMOUNT],
                           to_str_date(request[DATE])))
    elif request[REQUEST_TYPE] == STATS_REQUEST:
        print(stats_handler(request[DATE]))


def main() -> None:
    inp = input()
    while inp:
        request = request_parser(inp)
        request_handler(request)
        inp = input()


if __name__ == "__main__":
    main()
