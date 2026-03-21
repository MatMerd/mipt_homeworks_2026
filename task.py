#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"
COST_MASSIVE = []
INCOME_MASSIVE = []

EXPENSE_CATEGORIES = {
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

financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    if year % 4 == 0:
        if year % 100 != 0:
            return True
        if year % 400 == 0:
            return True
        return False
    return False


def get_days_in_month(month: int, year: int) -> int:
    if month == 2:
        if is_leap_year(year):
            return 29
        return 28
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    return 30


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: tuple формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    consist_of = maybe_dt.split("-")
    if len(consist_of) != 3:
        return None
    day = consist_of[0]
    month = consist_of[1]
    year = consist_of[2]
    if not (day.isdigit() and month.isdigit() and year.isdigit()):
        return None
    if not (1 <= int(month) <= 12):
        return None
    if not (1 <= int(day) <= get_days_in_month(int(month), int(year))):
        return None
    return int(day), int(month), int(year)


def is_correct_number(value: str) -> bool:
    if value.count(".") > 1:
        return False
    parts = value.split(".")
    if len(parts) == 1:
        return parts[0].isdigit()
    if len(parts) == 2:
        if parts[0] == "" or parts[1] == "":
            return False
        return parts[0].isdigit() and parts[1].isdigit()
    return False


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG
    financial_transactions_storage.append({"amount": amount, "date": income_date})
    INCOME_MASSIVE.append([income_date, amount])
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG
    financial_transactions_storage.append({"category": category_name, "amount": amount, "date": income_date})
    COST_MASSIVE.append([income_date, category_name, amount])
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    categories = []
    for elem in EXPENSE_CATEGORIES:
        for categorie in EXPENSE_CATEGORIES[elem]:
            categories.append(elem + "::" + categorie)
    return "\n".join(categories)


def category_handler(category_name: str) -> tuple[str, str] | None:
    pieces = category_name.split("::")
    if len(pieces) != 2:
        return None
    one_category = pieces[0]
    two_category = pieces[1]
    if one_category not in EXPENSE_CATEGORIES:
        return None
    if two_category not in EXPENSE_CATEGORIES[one_category]:
        return None
    return one_category, two_category


def amount_check(amount: float) -> str:
    if amount == int(amount):
        return str(int(amount))
    amount_str = str(amount)
    while amount_str[-1] == "0":
        amount_str = amount_str[:-1]
    if amount_str[-1] == ".":
        amount_str = amount_str[:-1]
    return amount_str


def stats_handler(report_date: str) -> str:
    our_date = extract_date(report_date)
    if our_date is None:
        return INCORRECT_DATE_MSG
    day, month, year = our_date
    income = 0.0
    cost = 0.0
    this_month_income = 0.0
    this_month_cost = 0.0
    categories = {}
    for elem in INCOME_MASSIVE:
        income_date = elem[0]
        amount = elem[1]
        income_day, income_month, income_year = extract_date(income_date)
        if (
                income_year < year
                or (income_year == year and income_month < month)
                or (income_year == year and income_month == month and income_day <= day)
        ):
            income += amount
        if income_year == year and income_month == month and income_day <= day:
            this_month_income += amount
    for elem in COST_MASSIVE:
        cost_date = elem[0]
        category = elem[1]
        amount = elem[2]
        cost_day, cost_month, cost_year = extract_date(cost_date)
        if (
                cost_year < year
                or (cost_year == year and cost_month < month)
                or (cost_year == year and cost_month == month and cost_day <= day)
        ):
            cost += amount
        if cost_year == year and cost_month == month and cost_day <= day:
            this_month_cost += amount
            if category not in categories:
                categories[category] = 0.0
            categories[category] += amount
    balance = income - cost
    maybe_profit = this_month_income - this_month_cost
    answer = []
    answer.append(f"Your statistics as of {report_date}:")
    answer.append(f"Total capital: {balance:.2f} rubles")
    if maybe_profit >= 0:
        answer.append(f"This month, the profit amounted to {maybe_profit:.2f} rubles.")
    else:
        answer.append(f"This month, the loss amounted to {abs(maybe_profit):.2f} rubles.")
    answer.append(f"Income: {this_month_income:.2f} rubles")
    answer.append(f"Expenses: {this_month_cost:.2f} rubles")
    answer.append("")
    answer.append("Details (category: amount):")
    sorted_categories = sorted(categories.keys())
    for i in range(len(sorted_categories)):
        category = sorted_categories[i]
        amount = categories[category]
        answer.append(f"{i + 1}. {category}: {amount_check(amount)}")
    return "\n".join(answer)


def response_to_request(request: list) -> str:
    if len(request) == 0:
        return UNKNOWN_COMMAND_MSG
    activity = request[0]
    if activity == "income":
        if len(request) != 3:
            return UNKNOWN_COMMAND_MSG
        amount_str = request[1].replace(",", ".")
        date = request[2]
        if not is_correct_number(amount_str):
            return NONPOSITIVE_VALUE_MSG
        amount = float(amount_str)
        if amount <= 0:
            return NONPOSITIVE_VALUE_MSG
        if extract_date(date) is None:
            return INCORRECT_DATE_MSG
        return income_handler(amount, date)
    elif activity == "cost":
        if len(request) == 2 and request[1] == "categories":
            return cost_categories_handler()
        if len(request) != 4:
            return UNKNOWN_COMMAND_MSG
        category = request[1]
        amount_str = request[2].replace(",", ".")
        date = request[3]
        if category_handler(category) is None:
            categories = cost_categories_handler()
            return NOT_EXISTS_CATEGORY + "\n" + categories
        if not is_correct_number(amount_str):
            return NONPOSITIVE_VALUE_MSG
        amount = float(amount_str)
        if amount <= 0:
            return NONPOSITIVE_VALUE_MSG
        if extract_date(date) is None:
            return INCORRECT_DATE_MSG
        return cost_handler(category, amount, date)
    elif activity == "stats":
        if len(request) != 2:
            return UNKNOWN_COMMAND_MSG
        date = request[1]
        if extract_date(date) is None:
            return INCORRECT_DATE_MSG
        return stats_handler(date)
    else:
        return UNKNOWN_COMMAND_MSG


def main() -> None:
    while True:
        line = input()
        if line == "":
            break
        request = line.split()
        print(response_to_request(request))


if __name__ == "__main__":
    main()

