#!/usr/bin/env python

from typing import Any, Optional, Tuple, List, Dict

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
    "Other": (),
}

# Константы
DAYS_IN_MONTH = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
FEBRUARY = 2
MIN_MONTH = 1
MAX_MONTH = 12
MIN_DAY = 1
DATE_PARTS_COUNT = 3
INCOME_ARGS_COUNT = 3
COST_ARGS_COUNT = 4
STATS_ARGS_COUNT = 2
COST_CATEGORIES_ARGS_COUNT = 2
CATEGORY_SEPARATOR = "::"

# Исправление 1: аннотация для EMPTY_DICT
EMPTY_DICT: Dict[str, Any] = {}

financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    """Определяет високосный год."""
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0


def get_days_in_month(month: int, year: int) -> int:
    """Возвращает количество дней в месяце."""
    if month == FEBRUARY and is_leap_year(year):
        return 29
    return DAYS_IN_MONTH[month - 1]


def validate_date(day: int, month: int, year: int) -> bool:
    """Проверяет корректность даты."""
    if month < MIN_MONTH or month > MAX_MONTH:
        return False
    if day < MIN_DAY or day > get_days_in_month(month, year):
        return False
    return year >= 1


def extract_date(maybe_dt: str) -> Optional[Tuple[int, int, int]]:
    """Парсит дату формата DD-MM-YYYY из строки."""
    parts = maybe_dt.split("-")
    if len(parts) != DATE_PARTS_COUNT:
        return None

    try:
        day = int(parts[0])
        month = int(parts[1])
        year = int(parts[2])
    except ValueError:
        return None

    if validate_date(day, month, year):
        return (day, month, year)
    return None


def parse_amount(amount_str: str) -> Optional[float]:
    """Парсит число из строки, заменяя запятую на точку."""
    normalized = amount_str.replace(",", ".")
    try:
        return float(normalized)
    except ValueError:
        return None


def save_invalid_transaction() -> None:
    """Сохраняет пустую транзакцию при ошибке."""
    financial_transactions_storage.append(EMPTY_DICT)


def is_invalid_category(category_name: str) -> bool:
    """Проверяет, существует ли категория."""
    if CATEGORY_SEPARATOR not in category_name:
        return True

    common_cat, specific_cat = category_name.split(CATEGORY_SEPARATOR, 1)
    if common_cat not in EXPENSE_CATEGORIES:
        return True

    if common_cat == "Other":
        return specific_cat != "Other"

    return specific_cat not in EXPENSE_CATEGORIES[common_cat]


def get_all_categories() -> list[str]:
    """Возвращает список всех доступных категорий."""
    categories = []
    for common_cat, subcategories in EXPENSE_CATEGORIES.items():
        for subcategory in subcategories:
            categories.append(f"{common_cat}{CATEGORY_SEPARATOR}{subcategory}")
    return categories


def income_handler(amount: float, income_date: str) -> str:
    """Обработчик дохода."""
    parsed_date = extract_date(income_date)

    if amount <= 0:
        save_invalid_transaction()
        return NONPOSITIVE_VALUE_MSG

    if parsed_date is None:
        save_invalid_transaction()
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({
        "amount": amount,
        "date": parsed_date,
    })
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, cost_date: str) -> str:
    """Обработчик расхода."""
    parsed_date = extract_date(cost_date)

    if is_invalid_category(category_name):
        save_invalid_transaction()
        return NOT_EXISTS_CATEGORY

    if amount <= 0:
        save_invalid_transaction()
        return NONPOSITIVE_VALUE_MSG

    if parsed_date is None:
        save_invalid_transaction()
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({
        "category": category_name,
        "amount": amount,
        "date": parsed_date,
    })
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    """Возвращает список всех доступных категорий."""
    categories = get_all_categories()
    return "\n".join(categories)


def is_earlier(date1: Tuple[int, int, int], date2: Tuple[int, int, int]) -> bool:
    """Проверяет, что date1 <= date2."""
    year1, month1, day1 = date1
    year2, month2, day2 = date2
    if year1 != year2:
        return year1 < year2
    if month1 != month2:
        return month1 < month2
    return day1 <= day2


def is_same_month(date1: Tuple[int, int, int], date2: Tuple[int, int, int]) -> bool:
    """Проверяет, что даты в одном месяце."""
    return date1[1] == date2[1] and date1[2] == date2[2]


# Исправление 2: аннотации для возвращаемых списков
def split_transactions() -> Tuple[List[Tuple[float, Tuple[int, int, int]]], 
                                   List[Tuple[str, float, Tuple[int, int, int]]]]:
    """Разделяет транзакции на доходы и расходы."""
    incomes: List[Tuple[float, Tuple[int, int, int]]] = []
    expenses: List[Tuple[str, float, Tuple[int, int, int]]] = []

    for transaction in financial_transactions_storage:
        if not transaction:
            continue

        amount = transaction.get("amount")
        date = transaction.get("date")

        if amount is None or date is None:
            continue

        category = transaction.get("category")
        if category is not None:
            # category is str, amount is float, date is tuple
            expenses.append((category, amount, date))  # type: ignore
        else:
            incomes.append((amount, date))  # type: ignore

    return incomes, expenses


# Исправление 3: аннотация для incomes параметра
def _calculate_income_stats(
    target_date: Tuple[int, int, int],
    incomes: List[Tuple[float, Tuple[int, int, int]]],
) -> Tuple[float, float]:
    """Рассчитывает статистику по доходам."""
    total_capital = 0.0
    month_income = 0.0

    for amount, date in incomes:
        if not is_earlier(date, target_date):
            continue
        total_capital += amount
        if is_same_month(date, target_date):
            month_income += amount

    return total_capital, month_income


# Исправление 4: аннотации для expenses параметра и возвращаемого dict
def _calculate_expense_stats(
    target_date: Tuple[int, int, int],
    expenses: List[Tuple[str, float, Tuple[int, int, int]]],
) -> Tuple[float, float, Dict[str, float]]:
    """Рассчитывает статистику по расходам."""
    total_capital = 0.0
    month_expense = 0.0
    # Исправление 5: аннотация для expense_by_category
    expense_by_category: Dict[str, float] = {}

    for category, amount, date in expenses:
        if not is_earlier(date, target_date):
            continue
        total_capital += amount
        if is_same_month(date, target_date):
            month_expense += amount
            expense_by_category[category] = expense_by_category.get(category, 0.0) + amount

    return total_capital, month_expense, expense_by_category


# Исправление 6: аннотация для expense_by_category параметра
def _build_statistics_string(
    report_date: str,
    total_capital: float,
    month_income: float,
    month_expense: float,
    expense_by_category: Dict[str, float],
) -> str:
    """Формирует строку со статистикой."""
    month_result = month_income - month_expense
    lines = [
        f"Your statistics as of {report_date}:",
        f"Total capital: {total_capital:.2f} rubles",
    ]

    if month_result >= 0:
        lines.append(f"This month, the profit amounted to {month_result:.2f} rubles.")
    else:
        lines.append(f"This month, the loss amounted to {abs(month_result):.2f} rubles.")

    lines.append(f"Income: {month_income:.2f} rubles")
    lines.append(f"Expenses: {month_expense:.2f} rubles")
    lines.append("Details (category: amount):")

    if expense_by_category:
        sorted_categories = sorted(expense_by_category.items())
        for idx, (category, amount) in enumerate(sorted_categories, 1):
            display_name = category.split(CATEGORY_SEPARATOR)[-1]
            if amount.is_integer():
                lines.append(f"{idx}. {display_name}: {int(amount)}")
            else:
                lines.append(f"{idx}. {display_name}: {amount}")

    return "\n".join(lines)


def stats_handler(report_date: str) -> str:
    """Обработчик статистики."""
    target_date = extract_date(report_date)
    if target_date is None:
        return INCORRECT_DATE_MSG

    incomes, expenses = split_transactions()

    income_capital, month_income = _calculate_income_stats(target_date, incomes)
    expense_capital, month_expense, expense_by_category = _calculate_expense_stats(
        target_date, expenses,
    )

    total_capital = income_capital - expense_capital

    return _build_statistics_string(
        report_date,
        total_capital,
        month_income,
        month_expense,
        expense_by_category,
    )


# Исправление 7: аннотация для parts параметра
def _handle_income(parts: List[str]) -> None:
    """Обрабатывает команду income."""
    if len(parts) != INCOME_ARGS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount = parse_amount(parts[1])
    if amount is None:
        print(UNKNOWN_COMMAND_MSG)
        return

    result = income_handler(amount, parts[2])
    print(result)


def _handle_cost_categories() -> None:
    """Обрабатывает команду cost categories."""
    print(cost_categories_handler())


# Исправление 8: аннотация для parts параметра
def _handle_cost_with_args(parts: List[str]) -> None:
    """Обрабатывает команду cost с аргументами."""
    amount = parse_amount(parts[2])
    if amount is None:
        print(UNKNOWN_COMMAND_MSG)
        return

    result = cost_handler(parts[1], amount, parts[3])
    print(result)


# Исправление 9: аннотация для parts параметра
def _handle_cost(parts: List[str]) -> None:
    """Обрабатывает команду cost."""
    if len(parts) == COST_CATEGORIES_ARGS_COUNT and parts[1].lower() == "categories":
        _handle_cost_categories()
    elif len(parts) == COST_ARGS_COUNT:
        _handle_cost_with_args(parts)
    else:
        print(UNKNOWN_COMMAND_MSG)


# Исправление 10: аннотация для parts параметра
def _handle_stats(parts: List[str]) -> None:
    """Обрабатывает команду stats."""
    if len(parts) != STATS_ARGS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return

    result = stats_handler(parts[1])
    print(result)


def main() -> None:
    """Главная функция программы."""
    while True:
        try:
            user_input = input().strip()
        except EOFError:
            break

        if not user_input:
            continue

        parts = user_input.split()
        if not parts:
            continue

        command = parts[0].lower()

        if command == "income":
            _handle_income(parts)
        elif command == "cost":
            _handle_cost(parts)
        elif command == "stats":
            _handle_stats(parts)
        else:
            print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()
