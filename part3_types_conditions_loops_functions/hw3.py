#!/usr/bin/env python
from __future__ import annotations

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"
AMOUNT_KEY = "amount"
DATE_KEY = "date"
CATEGORY_KEY = "category"
ZERO_AMOUNT = float()

DATE_LENGTH = 3
FEBRUARY_MONTH_NUMBER = 2
MONTHS_IN_YEAR = 12
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
Date = tuple[int, int, int]


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


def extract_date(maybe_dt: str) -> Date | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: tuple формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    raw_date_parts = maybe_dt.split("-")
    if len(raw_date_parts) != DATE_LENGTH:
        return None

    try:
        date_parts = [int(part) for part in raw_date_parts]
    except ValueError:
        return None

    day, month, year = date_parts
    if not (0 < month <= MONTHS_IN_YEAR):
        return None

    if not (0 < day <= get_days_in_month(month, year)):
        return None

    return day, month, year


def extract_amount(amount: str) -> float | None:
    """
        Парсит стоимость из строки.

        :param str amount: Проверяемая строка
        :return: float или None, если не является числом.
        :rtype: float | None
    """
    normalized_amount = amount.strip().replace(",", ".")
    try:
        parsed_amount = float(normalized_amount)
    except ValueError:
        return None
    else:
        if parsed_amount <= 0:
            return None
        return parsed_amount


def parse_date_argument(maybe_date: Date | str) -> Date | None:
    """
        Приводит дату к tuple-формату

        :param tuple[int, int, int] | str maybe_date: Дата в одном из поддерживаемых форматов
        :rtype: tuple[int, int, int] | None
    """
    if isinstance(maybe_date, str):
        return extract_date(maybe_date)
    return maybe_date


def add_empty_transaction() -> None:
    """
        Добавляет пустую транзакцию в хранилище

        :rtype: None
    """
    financial_transactions_storage.append({})


def save_income(amount: float, income_date: Date) -> None:
    """
        Сохраняет доход в хранилище

        :param float amount: Сумма
        :param tuple[int, int, int] income_date: Дата
        :rtype: None
    """
    financial_transactions_storage.append({AMOUNT_KEY: amount, DATE_KEY: income_date})


def save_cost(category_name: str, amount: float, cost_date: Date) -> None:
    """
        Сохраняет расход в хранилище

        :param str category_name: Категория
        :param float amount: Сумма
        :param tuple[int, int, int] cost_date: Дата
        :rtype: None
    """
    financial_transactions_storage.append({
        CATEGORY_KEY: category_name,
        AMOUNT_KEY: amount,
        DATE_KEY: cost_date,
    })


def income_handler(amount: float, income_date: Date | str) -> str:
    """
        Вносит данные в базу при использовании команды income

    :param int amount: Сумма
        :param tuple[int, int, int] income_date: Дата
        :rtype: str
    """
    if not isinstance(amount, (float, int)) or amount <= 0:
        add_empty_transaction()
        return NONPOSITIVE_VALUE_MSG

    parsed_income_date = parse_date_argument(income_date)
    if parsed_income_date is None:
        add_empty_transaction()
        return INCORRECT_DATE_MSG

    save_income(amount, parsed_income_date)
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


def cost_handler(category_name: str, amount: float, income_date: Date | str) -> str:
    """
        Вносит данные в базу при использовании команды cost

        :param str category_name: Название категории
        :param float amount: Сумма
    :param tuple[int, int, int] income_date: Дата
        :rtype: str
    """
    if not is_category_exists(category_name):
        add_empty_transaction()
        return NOT_EXISTS_CATEGORY

    if not isinstance(amount, (float, int)) or amount <= 0:
        add_empty_transaction()
        return NONPOSITIVE_VALUE_MSG

    parsed_income_date = parse_date_argument(income_date)
    if parsed_income_date is None:
        add_empty_transaction()
        return INCORRECT_DATE_MSG

    save_cost(category_name, amount, parsed_income_date)
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


def get_day(date: Date) -> int:
    """
        Возвращает день из даты

        :param tuple[int, int, int] date: Дата
        :rtype: int
    """
    return date[0]


def get_month(date: Date) -> int:
    """
        Возвращает месяц из даты

        :param tuple[int, int, int] date: Дата
        :rtype: int
    """
    return date[1]


def get_year(date: Date) -> int:
    """
        Возвращает год из даты

        :param tuple[int, int, int] date: Дата
        :rtype: int
    """
    return date[2]


def beautify_date(date: Date) -> str:
    """
        Приводит дату к читаемому виду

        :param tuple[int, int, int] date: Дата
        :rtype: str
    """
    day = get_day(date)
    month = get_month(date)
    year = get_year(date)
    return f"{day:02d}-{month:02d}-{year:04d}"


def get_category_sort_key(item: tuple[str, float]) -> str:
    """
        Возвращает ключ сортировки для категорий

        :param tuple[str, float] item: Пара категория-сумма
        :rtype: str
    """
    category_name, _ = item
    return category_name.lower()


def print_stats_by_categories(data: dict[str, float]) -> None:
    """
        Приводит хранящиеся траты по категориям к читаемому виду

        :param dict[str, float] data: Данные
        :rtype: None
    """
    categories = sorted(data.items(), key=get_category_sort_key)

    for index, (category, amount) in enumerate(categories, start=1):
        print(f"{index}. {category}: {format_amount(amount)}")


def is_same_month(first_date: Date, second_date: Date) -> bool:
    """
        Проверяет, что даты находятся в одном месяце одного года

        :param tuple[int, int, int] first_date: Первая дата
        :param tuple[int, int, int] second_date: Вторая дата
        :rtype: bool
    """
    first_month = get_month(first_date)
    second_month = get_month(second_date)
    if first_month != second_month:
        return False
    return get_year(first_date) == get_year(second_date)


def is_date_not_later(first_date: Date, second_date: Date) -> bool:
    """
        Проверяет, что первая дата не позже второй

        :param tuple[int, int, int] first_date: Первая дата
        :param tuple[int, int, int] second_date: Вторая дата
        :rtype: bool
    """
    first_date_parts = (get_year(first_date), get_month(first_date), get_day(first_date))
    second_date_parts = (get_year(second_date), get_month(second_date), get_day(second_date))
    return first_date_parts <= second_date_parts


def has_transaction_date(transaction: dict[str, Any]) -> bool:
    """
        Проверяет наличие даты в транзакции

        :param dict[str, Any] transaction: Транзакция
        :rtype: bool
    """
    return DATE_KEY in transaction


def is_expense(transaction: dict[str, Any]) -> bool:
    """
        Проверяет, является ли транзакция расходом

        :param dict[str, Any] transaction: Транзакция
        :rtype: bool
    """
    return CATEGORY_KEY in transaction


def is_transaction_in_report_period(transaction: dict[str, Any], report_date: Date) -> bool:
    """
        Проверяет, попадает ли транзакция в отчетный месяц

        :param dict[str, Any] transaction: Транзакция
        :param tuple[int, int, int] report_date: Дата отчета
        :rtype: bool
    """
    if not has_transaction_date(transaction):
        return False

    transaction_date = transaction[DATE_KEY]
    if not is_same_month(transaction_date, report_date):
        return False
    return is_date_not_later(transaction_date, report_date)


def calculate_total_capital(report_date: Date) -> float:
    """
        Расчет накопленной суммы

        :rtype: float
    """
    total_capital = ZERO_AMOUNT
    for transaction in financial_transactions_storage:
        if not has_transaction_date(transaction):
            continue

        if not is_date_not_later(transaction[DATE_KEY], report_date):
            continue

        amount = transaction[AMOUNT_KEY]
        if is_expense(transaction):
            total_capital -= amount
        else:
            total_capital += amount
    return total_capital


def calculate_income_expenses(transaction: dict[str, Any], date: Date) -> tuple[float, float]:
    """
        Вычисление статистики за дату.
        Возвращается: income, expenses.

        :param dict[str, Any] transaction: Транзакция
        :param tuple[int, int, int] date: Дата
        :rtype: tuple[float, float]
    """
    if not is_transaction_in_report_period(transaction, date):
        return ZERO_AMOUNT, ZERO_AMOUNT

    amount = transaction[AMOUNT_KEY]
    if is_expense(transaction):
        return ZERO_AMOUNT, amount
    return amount, ZERO_AMOUNT


def get_data(report_date: Date) -> dict[str, float]:
    """
        Собирает статистику по категориям за месяц

        :param tuple[int, int, int] report_date: Дата отчета
        :rtype: dict[str, float]
    """
    data: dict[str, float] = {}
    for transaction in financial_transactions_storage:
        if not is_expense(transaction):
            continue

        if not is_transaction_in_report_period(transaction, report_date):
            continue

        child_category = get_child_category(transaction[CATEGORY_KEY])
        category_total = data.get(child_category, ZERO_AMOUNT)
        data[child_category] = category_total + transaction[AMOUNT_KEY]
    return data


def format_amount(amount: float) -> str:
    """
        Форматирует число для вывода

        :param float amount: Сумма
        :rtype: str
    """
    return f"{amount:.2f}"


def calculate_stats(date: Date) -> tuple[float, float]:
    """
        Вычисление статистики за дату.
        Возвращается: income, expenses.

        :param tuple[int, int, int] date: Дата
        :rtype: tuple[float, float]
    """
    total_income = ZERO_AMOUNT
    total_expenses = ZERO_AMOUNT
    for transaction in financial_transactions_storage:
        income, expenses = calculate_income_expenses(transaction, date)
        total_income += income
        total_expenses += expenses
    return total_income, total_expenses


def get_result_type(income: float, expenses: float) -> str:
    """
        Определяет тип финансового результата

        :param float income: Доходы
        :param float expenses: Расходы
        :rtype: str
    """
    if income - expenses < 0:
        return "loss"
    return "profit"


def stats_handler(report_date: Date) -> None:
    """
        Вывод данных команды stats

        :param tuple[int, int, int] report_date: Дата, за которую нужно получить отчет
        :rtype: None
    """
    income, expenses = calculate_stats(report_date)
    result_type = get_result_type(income, expenses)
    month_result = format_amount(abs(income - expenses))

    print(f"Your statistics as of {beautify_date(report_date)}:")
    print(f"Total capital: {format_amount(calculate_total_capital(report_date))} rubles")
    print(f"This month, the {result_type} amounted to {month_result} rubles.")
    print(f"Income: {format_amount(income)} rubles")
    print(f"Expenses: {format_amount(expenses)} rubles")
    print("\nDetails (category: amount):")
    print_stats_by_categories(get_data(report_date))


def main() -> None:
    for command in iter(input, ""):
        listen(command)


if __name__ == "__main__":
    main()
