#!/usr/bin/env python

from typing import Any

# Сообщения для вывода
UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

# Константы для ключей словаря
AMOUNT_KEY = "amount"
DATE_KEY = "date"
CATEGORY_KEY = "category"
ZERO_AMOUNT = float(0)

# Тип для даты
Date = tuple[int, int, int]

# Словарь категорий
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

# Глобальное хранилище всех транзакций
financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    # Проверяю високосный ли год
    if year % 100 == 0:
        return year % 400 == 0
    return year % 4 == 0


def get_days_in_month(month: int, year: int) -> int:
    # Возвращаю сколько дней в месяце
    if month == 2:  # февраль
        return 29 if is_leap_year(year) else 28
    if month in [4, 6, 9, 11]:  # месяцы с 30 днями
        return 30
    return 31


def extract_date(maybe_dt: str) -> Date | None:
    # Парсю дату DD-MM-YYYY из строки.
    parts = maybe_dt.split('-')
    if len(parts) != 3:
        return None
    
    day_str, month_str, year_str = parts
    
    # проверяю длину частей (DD-MM-YYYY)
    if len(day_str) != 2 or len(month_str) != 2 or len(year_str) != 4:
        return None
    
    # проверяю что все цифры
    if not (day_str.isdigit() and month_str.isdigit() and year_str.isdigit()):
        return None
    
    day = int(day_str)
    month = int(month_str)
    year = int(year_str)
    
    # проверяю диапазон месяца
    if month < 1 or month > 12:
        return None
    
    # проверяю день с учетом количества дней в месяце
    max_days = get_days_in_month(month, year)
    if day < 1 or day > max_days:
        return None
    
    return (day, month, year)


def is_valid_category(category_name: str) -> bool:
    # Проверяю существует ли категория
    parts = category_name.split("::")
    if len(parts) != 2:
        return False
    
    common_category, target_category = parts
    # проверяю что общая категория есть и целевая в её списке
    return (common_category in EXPENSE_CATEGORIES and 
            target_category in EXPENSE_CATEGORIES[common_category])


def date_to_comparable(date_value: Date) -> Date:
    # Конвертирую (day, month, year) в (year, month, day)
    day, month, year = date_value
    return (year, month, day)


def is_before(date_left: Date, date_right: Date) -> bool:
    # Проверяю что date_left < date_right
    return date_to_comparable(date_left) < date_to_comparable(date_right)


def save_error(error_message: str) -> str:
    # Добавляю пустую запись при ошибке и возвращает сообщение
    financial_transactions_storage.append({})
    return error_message


def save_income(amount: float, parsed_date: Date) -> str:
    # Сохраняю доход в хранилище
    financial_transactions_storage.append({
        AMOUNT_KEY: amount,
        DATE_KEY: parsed_date
    })
    return OP_SUCCESS_MSG


def income_handler(amount: float, income_date: str) -> str:
    # Обработчик команды income
    # сначала проверяю сумму
    if amount <= 0:
        return save_error(NONPOSITIVE_VALUE_MSG)
    
    # потом дату
    parsed_date = extract_date(income_date)
    if parsed_date is None:
        return save_error(INCORRECT_DATE_MSG)
    
    # если все ок, то сохраняю
    return save_income(amount, parsed_date)


def save_cost(category_name: str, amount: float, parsed_date: Date) -> str:
    # Сохраняю расход в хранилище
    financial_transactions_storage.append({
        CATEGORY_KEY: category_name,
        AMOUNT_KEY: amount,
        DATE_KEY: parsed_date
    })
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    # Обработчик команды cost
    # проверяю сумму
    if amount <= 0:
        return save_error(NONPOSITIVE_VALUE_MSG)
    
    # проверяю дату
    parsed_date = extract_date(income_date)
    if parsed_date is None:
        return save_error(INCORRECT_DATE_MSG)
    
    # проверяю категорию
    if not is_valid_category(category_name):
        return save_error(NOT_EXISTS_CATEGORY)
    
    # сохраняю
    return save_cost(category_name, amount, parsed_date)


def cost_categories_handler() -> str:
    # Возвращаю список всех категорий
    categories: list[str] = []
    for common_category, target_categories in EXPENSE_CATEGORIES.items():
        for target_category in target_categories:
            categories.append(f"{common_category}::{target_category}")
    return "\n".join(categories)


def update_category_details(category_details: dict[str, float], category: str, amount: float) -> None:
    # Обновляю сумму по категории
    if category not in category_details:
        category_details[category] = ZERO_AMOUNT
    category_details[category] += amount


def handle_stats_item(
    item: dict[str, Any],
    report_date: Date,
    category_details: dict[str, float],
) -> tuple[float, float]:
    # Обрабатываю одну транзакцию для статистики
    item_date = item.get(DATE_KEY)
    
    if not item_date or item_date is None or not is_before(item_date, report_date):
        return ZERO_AMOUNT, ZERO_AMOUNT
    
    amount = item.get(AMOUNT_KEY)
    if amount is None:
        return ZERO_AMOUNT, ZERO_AMOUNT
    
    category = item.get(CATEGORY_KEY)
    if category is None:
        return ZERO_AMOUNT, amount
    
    update_category_details(category_details, category, amount)
    return amount, ZERO_AMOUNT


def collect_stats(report_date: Date) -> tuple[float, float, dict[str, float]]:
    """
    Собираю статистику до указанной даты.
    Возвращаю (сумма расходов, сумма доходов, словарь категорий)
    """
    costs_amount = ZERO_AMOUNT
    incomes_amount = ZERO_AMOUNT
    category_details: dict[str, float] = {}
    
    for item in financial_transactions_storage:
        item_costs, item_incomes = handle_stats_item(item, report_date, category_details)
        costs_amount += item_costs
        incomes_amount += item_incomes
    
    return costs_amount, incomes_amount, category_details


def render_details(category_details: dict[str, float]) -> str:
    # Форматирую детали по категориям для вывода
    details = []
    for index, (category, amount) in enumerate(category_details.items()):
        details.append(f"{index}. {category}: {amount}")
    return "\n".join(details)


def stats_handler(report_date: str) -> str:
    # Обработчик команды stats
    parsed_report_date = extract_date(report_date)
    if parsed_report_date is None:
        return INCORRECT_DATE_MSG
    
    # собираю статистику
    costs_amount, incomes_amount, category_details = collect_stats(parsed_report_date)
    
    # считаю общий капитал
    total_capital = costs_amount - incomes_amount
    amount_word = "loss" if total_capital < 0 else "profit"
    
    # формирую вывод
    return (
        f"Your statistics as of {report_date}:\n"
        f"Total capital: {total_capital:.2f} rubles\n"
        f"This month, the {amount_word} amounted to {total_capital:.2f} rubles.\n"
        f"Income: {costs_amount:.2f} rubles\n"
        f"Expenses: {incomes_amount:.2f} rubles\n\n"
        f"Details (category: amount):\n"
        f"{render_details(category_details)}\n"
    )


def parse_amount(raw_amount: str) -> float:
    """Парсит сумму из строки (заменяет запятую на точку)"""
    return float(raw_amount.replace(",", "."))


def handle_income_command(command_parts: list[str]) -> str:
    """Обрабатывает команду income"""
    if len(command_parts) != 3:
        return UNKNOWN_COMMAND_MSG
    
    amount = parse_amount(command_parts[1])
    return income_handler(amount, command_parts[2])


def handle_cost_command(command_parts: list[str]) -> str:
    """Обрабатывает команду cost"""
    if len(command_parts) == 2 and command_parts[1] == "categories":
        return cost_categories_handler()
    
    if len(command_parts) != 4:
        return UNKNOWN_COMMAND_MSG
    
    amount = parse_amount(command_parts[2])
    result = cost_handler(command_parts[1], amount, command_parts[3])
    
    # если категория не существует, вывожу список категорий
    if result == NOT_EXISTS_CATEGORY:
        return f"{result}\n{cost_categories_handler()}"
    
    return result


def handle_command(command: str) -> str:
    # Обрабатываю команду
    command_parts = command.split()
    if not command_parts:
        return UNKNOWN_COMMAND_MSG
    
    cmd = command_parts[0]
    
    if cmd == "income":
        return handle_income_command(command_parts)
    elif cmd == "cost":
        return handle_cost_command(command_parts)
    elif cmd == "stats" and len(command_parts) == 2:
        return stats_handler(command_parts[1])
    else:
        return UNKNOWN_COMMAND_MSG


def main() -> None:
    # Главный цикл программы
    command = input()
    while command:
        if command == "exit":
            return
        
        print(handle_command(command))
        command = input()


if __name__ == "__main__":
    main()
