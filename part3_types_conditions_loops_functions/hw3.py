#!/usr/bin/env python

from typing import Any

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


financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).
    """
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    if year % 4 == 0:
        return True
    return False


def get_days_in_month(month: int, year: int) -> int:
    """
    Возвращает количество дней в месяце для заданного года.
    """
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if month == 2 and is_leap_year(year):
        return 29
    return days_in_month[month - 1]


def validate_date(day: int, month: int, year: int) -> bool:
    """
    Проверяет корректность даты.
    """
    if month < 1 or month > 12:
        return False
    if day < 1 or day > get_days_in_month(month, year):
        return False
    if year < 1:
        return False
    return True


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.
    """
    parts = maybe_dt.split('-')
    if len(parts) != 3:
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


def parse_amount(amount_str: str) -> float | None:
    """
    Парсит число из строки, заменяя запятую на точку.
    """
    amount_str = amount_str.replace(',', '.')
    try:
        amount = float(amount_str)
        return amount
    except ValueError:
        return None


def get_all_categories() -> list[str]:
    """
    Возвращает список всех доступных категорий в формате common_category::target_category
    Сортировка по common_category, затем по target_category
    """
    categories = []
    # Сортируем ключи для правильного порядка вывода
    for common in sorted(EXPENSE_CATEGORIES.keys()):
        targets = EXPENSE_CATEGORIES[common]
        if targets:
            # Сортируем подкатегории
            for target in sorted(targets):
                categories.append(f"{common}::{target}")
        else:
            categories.append(common)
    return categories


def validate_category(category_str: str) -> bool:
    """
    Проверяет существование категории.
    """
    if '::' in category_str:
        common, target = category_str.split('::', 1)
        if common in EXPENSE_CATEGORIES:
            return target in EXPENSE_CATEGORIES[common]
    return False


def income_handler(amount: float, income_date: str) -> str:
    """
    Обработчик дохода.
    """
    date_tuple = extract_date(income_date)
    if date_tuple is None:
        return INCORRECT_DATE_MSG
    
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG
    
    financial_transactions_storage.append({
        "type": "income",
        "amount": amount,
        "date": date_tuple,  # Сохраняем как кортеж, а не строку
        "date_str": income_date
    })
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, cost_date: str) -> str:
    """
    Обработчик расхода.
    """
    date_tuple = extract_date(cost_date)
    if date_tuple is None:
        return INCORRECT_DATE_MSG
    
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG
    
    if not validate_category(category_name):
        categories_list = get_all_categories()
        return f"{NOT_EXISTS_CATEGORY}\nAvailable categories:\n" + "\n".join(categories_list)
    
    financial_transactions_storage.append({
        "type": "expense",
        "category": category_name,
        "amount": amount,
        "date": date_tuple,  # Сохраняем как кортеж
        "date_str": cost_date
    })
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    """
    Возвращает список всех доступных категорий.
    """
    categories = get_all_categories()
    return "\n".join(categories)


def get_month_transactions(transactions: list, target_date: tuple[int, int, int]) -> tuple[list, list]:
    """
    Возвращает доходы и расходы за месяц указанной даты.
    """
    month_incomes = []
    month_expenses = []
    
    for t in transactions:
        t_day, t_month, t_year = t["date"]
        if t_month == target_date[1] and t_year == target_date[2]:
            if t["type"] == "income":
                month_incomes.append(t)
            else:
                month_expenses.append(t)
    
    return month_incomes, month_expenses


def get_all_transactions_until_date(transactions: list, target_date: tuple[int, int, int]) -> list:
    """
    Возвращает все транзакции до указанной даты (включительно).
    """
    result = []
    for t in transactions:
        t_day, t_month, t_year = t["date"]
        target_day, target_month, target_year = target_date
        
        if t_year < target_year:
            result.append(t)
        elif t_year == target_year:
            if t_month < target_month:
                result.append(t)
            elif t_month == target_month:
                if t_day <= target_day:
                    result.append(t)
    return result


def calculate_total_capital(transactions: list) -> float:
    """
    Рассчитывает суммарный капитал.
    """
    total = 0.0
    for t in transactions:
        if t["type"] == "income":
            total += t["amount"]
        else:
            total -= t["amount"]
    return total


def get_expenses_by_category(expenses: list) -> dict:
    """
    Группирует расходы по категориям.
    """
    categories_sum = {}
    for expense in expenses:
        cat = expense["category"]
        categories_sum[cat] = categories_sum.get(cat, 0.0) + expense["amount"]
    return categories_sum


def stats_handler(report_date: str) -> str:
    """
    Обработчик статистики.
    """
    date_tuple = extract_date(report_date)
    if date_tuple is None:
        return INCORRECT_DATE_MSG
    
    day, month, year = date_tuple
    
    # Получаем все транзакции до указанной даты
    all_until_date = get_all_transactions_until_date(financial_transactions_storage, date_tuple)
    total_capital = calculate_total_capital(all_until_date)
    
    # Получаем транзакции за текущий месяц
    month_incomes, month_expenses = get_month_transactions(financial_transactions_storage, date_tuple)
    
    total_income = sum(t["amount"] for t in month_incomes)
    total_expenses = sum(t["amount"] for t in month_expenses)
    month_result = total_income - total_expenses
    
    # Формируем результат
    result = f"Your statistics as of {report_date}:\n"
    result += f"Total capital: {total_capital:.2f} rubles\n"
    
    if month_result >= 0:
        result += f"This month, the profit amounted to {month_result:.2f} rubles.\n"
    else:
        result += f"This month, the loss amounted to {abs(month_result):.2f} rubles.\n"
    
    result += f"Income: {total_income:.2f} rubles\n"
    result += f"Expenses: {total_expenses:.2f} rubles\n"
    
    # Детализация по категориям
    expenses_by_cat = get_expenses_by_category(month_expenses)
    if expenses_by_cat:
        result += "Details (category: amount):\n"
        sorted_categories = sorted(expenses_by_cat.items())
        for idx, (cat, amount) in enumerate(sorted_categories, 1):
            # Извлекаем только target_category для отображения
            display_cat = cat.split('::')[-1] if '::' in cat else cat
            # Форматируем сумму без десятичных знаков, если это целое число
            if amount == int(amount):
                result += f"{idx}. {display_cat}: {int(amount)}\n"
            else:
                result += f"{idx}. {display_cat}: {amount}\n"
    else:
        result += "Details (category: amount):\n"
    
    return result.rstrip('\n')


def main() -> None:
    """
    Главная функция программы.
    """
    while True:
        try:
            user_input = input().strip()
        except EOFError:
            break
        
        if not user_input:
            continue
        
        parts = user_input.split()
        command = parts[0].lower() if parts else ""
        
        if command == "income":
            if len(parts) != 3:
                print(UNKNOWN_COMMAND_MSG)
                continue
            
            amount_str = parts[1]
            date_str = parts[2]
            
            amount = parse_amount(amount_str)
            if amount is None:
                print(UNKNOWN_COMMAND_MSG)
                continue
            
            result = income_handler(amount, date_str)
            print(result)
        
        elif command == "cost":
            if len(parts) == 2 and parts[1].lower() == "categories":
                print(cost_categories_handler())
            elif len(parts) == 4:
                category = parts[1]
                amount_str = parts[2]
                date_str = parts[3]
                
                amount = parse_amount(amount_str)
                if amount is None:
                    print(UNKNOWN_COMMAND_MSG)
                    continue
                
                result = cost_handler(category, amount, date_str)
                print(result)
            else:
                print(UNKNOWN_COMMAND_MSG)
        
        elif command == "stats":
            if len(parts) != 2:
                print(UNKNOWN_COMMAND_MSG)
                continue
            
            date_str = parts[1]
            result = stats_handler(date_str)
            print(result)
        
        else:
            print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()
