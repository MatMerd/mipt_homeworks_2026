#!/usr/bin/env python
from __future__ import annotations

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

DATE_LENGTH = 3
FEBRUARY_MONTH_NUMBER = 2
MONTH_LAST_DAY = (
    31, 28, 31, 30, 31, 30,
    31, 31, 30, 31, 30, 31
)
INCOME_ARGS_LENGTH = 2
CATEGORY_LAYER_COUNT = 2
COST_ARGS_LENGTH = 3
STATS_ARGS_LENGTH = 1

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
    if year % 4 == 0 and year % 100 != 0:
        return True
    return year % 400 == 0


def get_days_in_month(month: int, year: int) -> int:
    """
        Для заданного месяца и года определяет последний день месяца

        :param int month: Номер месяца
        :param int year: Номер года
        :return: Количество дней в месяце
        :rtype: int
    """
    if month == FEBRUARY_MONTH_NUMBER:
        if is_leap_year(year):
            return 29
        return 28
    return MONTH_LAST_DAY[month - 1]


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: tuple формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    str_date = maybe_dt.split("-")
    if len(str_date) != DATE_LENGTH:
        return None

    try:
        str_date = list(map(int, str_date))
        if not (0 < str_date[1] < 13 and 0 < str_date[0] <= get_days_in_month(str_date[1], str_date[2])):
            return None
    except ValueError:
        return None
    return str_date[0], str_date[1], str_date[2]


def extract_amount(amount: str) -> float | None:
    """
        Парсит стоимость из строки.

        :param str amount: Проверяемая строка
        :return: float или None, если не является числом.
        :rtype: float | None
    """
    amount = amount.strip().replace(",", ".")
    try:
        amount = float(amount)
        if amount <= 0:
            return None
        return amount
    except ValueError:
        return None


def income_handler(amount: float, income_date: tuple[int, int, int] | str) -> str:
    """
        Вносит данные в базу при использовании команды income

        :param int amount: Сумма
        :param tuple[int, int, int] income_date: Дата
        :rtype: str
    """
    if not isinstance(amount, (float, int)) or amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    if isinstance(income_date, str):
        income_date = extract_date(income_date)

    if income_date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({"amount": amount, "date": income_date})
    return OP_SUCCESS_MSG


def listen(command: str) -> None:
    """
        Первичный обработчик команд

        :param str command: Строка команды
        :rtype: None
    """
    command_line = command.strip().split()
    if not command_line:
        print(UNKNOWN_COMMAND_MSG)
        return

    if command_line[0].lower() == "income":
        income_listener(command_line[1:])
    elif command_line[0].lower() == "cost":
        cost_listener(command_line[1:])
    elif command_line[0].lower() == "stats":
        stats_listener(command_line[1:])
    else:
        print(UNKNOWN_COMMAND_MSG)


def income_listener(args: list[str]) -> None:
    """
        Обработка команды income

        :param list[str] args: Аргументы команды
        :rtype: None
    """
    if len(args) != INCOME_ARGS_LENGTH:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount = extract_amount(args[0])
    if amount is None:
        print(NONPOSITIVE_VALUE_MSG)
        return

    date = extract_date(args[1])
    if date is None:
        print(INCORRECT_DATE_MSG)
        return

    print(income_handler(amount, date))


def is_category_exists(category_name: str) -> bool:
    """
        Проверка, существует ли такая категория

        :param str category_name: Проверяемая категроия
        :rtype: bool
    """
    category_layers = category_name.split("::")
    if len(category_layers) != CATEGORY_LAYER_COUNT:
        return False

    main_category, child_category = category_layers
    return main_category in EXPENSE_CATEGORIES and child_category in EXPENSE_CATEGORIES[main_category]


def get_child_category(category_name: str) -> str:
    """
        Возвращает дочернюю категорию

        :param str category_name: Проверяемая категроия
        :rtype: str
    """
    return category_name.split("::")[-1]


def cost_handler(category_name: str, amount: float, income_date: tuple[int, int, int] | str) -> str:
    """
        Вносит данные в базу при использовании команды cost

        :param str category_name: Название категории
        :param float amount: Сумма
        :param tuple[int, int, int] income_date: Дата
        :rtype: str
    """
    if not is_category_exists(category_name):
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY

    if not isinstance(amount, (float, int)) or amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    if isinstance(income_date, str):
        income_date = extract_date(income_date)

    if income_date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({"category": category_name, "amount": amount, "date": income_date})
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    """
        Обработка команды cost categories
    """
    return "\n".join([
        f"{main_category}::{child_category}"
        for main_category, child_categories in EXPENSE_CATEGORIES.items()
        for child_category in child_categories
    ])


def cost_listener(args: list[str]) -> None:
    """
        Обработка команды cost

        :param list[str] args: Аргументы команды
        :rtype: None
    """
    if not args:
        print(UNKNOWN_COMMAND_MSG)
        return

    if args[0].lower() == "categories" and len(args) == 1:
        print(cost_categories_handler())
    else:
        if len(args) != COST_ARGS_LENGTH:
            print(UNKNOWN_COMMAND_MSG)
            return

        if not is_category_exists(args[0]):
            print(NOT_EXISTS_CATEGORY)
            print(cost_categories_handler())
            return

        amount = extract_amount(args[1])
        if amount is None:
            print(NONPOSITIVE_VALUE_MSG)
            return

        date = extract_date(args[2])
        if date is None:
            print(INCORRECT_DATE_MSG)
            return

        print(cost_handler(args[0], amount, date))


def stats_listener(args: list[str]) -> None:
    """
        Обработка команды stats

        :param list[str] args: Аргументы команды
        :rtype: None
    """
    if len(args) != STATS_ARGS_LENGTH:
        print(UNKNOWN_COMMAND_MSG)
        return

    date = extract_date(args[0])
    if date is None:
        print(INCORRECT_DATE_MSG)
        return

    stats_handler(date)


def beautify_date(date: tuple[int, int, int]) -> str:
    """
        Приводит дату к читаемому виду

        :param tuple[int, int, int] date: Дата
        :rtype: str
    """
    return f"{date[0]:02d}-{date[1]:02d}-{date[2]:04d}"


def print_stats_by_categories(data: dict[str, float]) -> None:
    """
        Приводит хранящиеся траты по категориям к читаемому виду

        :param dict[str, float] data: Данные
        :rtype: None
    """
    categories = sorted(data.items(), key=lambda x: x[0].lower())

    for index, (category, amount) in enumerate(categories, start=1):
        print(f"{index}. {category}: {format_amount(amount)}")


def is_same_month(first_date: tuple[int, int, int], second_date: tuple[int, int, int]) -> bool:
    """
        Проверяет, что даты находятся в одном месяце одного года

        :param tuple[int, int, int] first_date: Первая дата
        :param tuple[int, int, int] second_date: Вторая дата
        :rtype: bool
    """
    return first_date[1] == second_date[1] and first_date[2] == second_date[2]


def is_date_not_later(first_date: tuple[int, int, int], second_date: tuple[int, int, int]) -> bool:
    """
        Проверяет, что первая дата не позже второй

        :param tuple[int, int, int] first_date: Первая дата
        :param tuple[int, int, int] second_date: Вторая дата
        :rtype: bool
    """
    return (first_date[2], first_date[1], first_date[0]) <= (second_date[2], second_date[1], second_date[0])


def calculate_total_capital(report_date: tuple[int, int, int]) -> float:
    """
        Расчет накопленной суммы

        :rtype: float
    """
    total_capital = 0.0
    for transaction in financial_transactions_storage:
        if "date" not in transaction or not is_date_not_later(transaction["date"], report_date):
            continue

        amount = transaction["amount"]
        if "category" in transaction:
            total_capital -= amount
        else:
            total_capital += amount
    return total_capital


def calculate_income_expenses(transaction: dict[str, Any], date: tuple[int, int, int]) -> tuple[float, float]:
    """
        Вычисление статистики за дату.
        Возвращается: income, expenses.

        :param dict[str, Any] transaction: Транзакция
        :param tuple[int, int, int] date: Дата
        :rtype: tuple[float, float]
    """
    if "date" not in transaction:
        return 0.0, 0.0

    transaction_date = transaction["date"]
    if not is_same_month(transaction_date, date) or not is_date_not_later(transaction_date, date):
        return 0.0, 0.0

    amount = transaction["amount"]
    if "category" in transaction:
        return 0.0, amount
    return amount, 0.0


def get_data(report_date: tuple[int, int, int]) -> dict[str, float]:
    """
        Собирает статистику по категориям за месяц

        :param tuple[int, int, int] report_date: Дата отчета
        :rtype: dict[str, float]
    """
    data: dict[str, float] = {}
    for transaction in financial_transactions_storage:
        if "category" not in transaction or "date" not in transaction:
            continue

        if not is_same_month(transaction["date"], report_date) or not is_date_not_later(transaction["date"], report_date):
            continue

        child_category = get_child_category(transaction["category"])
        data[child_category] = data.get(child_category, 0.0) + transaction["amount"]
    return data


def format_amount(amount: float) -> str:
    """
        Форматирует число для вывода

        :param float amount: Сумма
        :rtype: str
    """
    return f"{amount:.2f}"


def calculate_stats(date: tuple[int, int, int]) -> tuple[float, float]:
    """
        Вычисление статистики за дату.
        Возвращается: income, expenses.

        :param tuple[int, int, int] date: Дата
        :rtype: tuple[float, float]
    """
    total_income = 0.0
    total_expenses = 0.0
    for transaction in financial_transactions_storage:
        income, expenses = calculate_income_expenses(transaction, date)
        total_income += income
        total_expenses += expenses
    return total_income, total_expenses


def stats_handler(report_date: tuple[int, int, int]) -> None:
    """
        Вывод данных команды stats

    :param tuple[int, int, int] report_date: Дата, за которую нужно получить отчет
        :rtype: None
    """
    date = beautify_date(report_date)
    capital = calculate_total_capital(report_date)
    data = get_data(report_date)
    income, expenses = calculate_stats(report_date)
    result_type = "loss" if income - expenses < 0 else "profit"

    print(f"Your statistics as of {date}:")
    print(f"Total capital: {format_amount(capital)} rubles")
    print(f"This month, the {result_type} amounted to {format_amount(abs(income - expenses))} rubles.")
    print(f"Income: {format_amount(income)} rubles")
    print(f"Expenses: {format_amount(expenses)} rubles")
    print("\nDetails (category: amount):")
    print_stats_by_categories(data)



def main() -> None:
    while True:
        command = input()
        listen(command)


if __name__ == "__main__":
    main()
