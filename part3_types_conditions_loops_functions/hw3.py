#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

# Константы для магических чисел
FEBRUARY = 2
DAYS_IN_MONTH_COUNT = 12
DATE_PARTS_COUNT = 3
INCOME_ARGS_COUNT = 3
COST_CATEGORIES_ARGS_COUNT = 2
COST_FULL_ARGS_COUNT = 4
STATS_ARGS_COUNT = 2

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
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    if year % 4 == 0:
        return True
    return False


def get_days_in_month(month: int, year: int) -> int:
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    if month == FEBRUARY and is_leap_year(year):
        return 29
    return days_in_month[month - 1]


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    parts = maybe_dt.split('-')
    
    if len(parts) != DATE_PARTS_COUNT:
        return None
    
    try:
        day = int(parts[0])
        month = int(parts[1])
        year = int(parts[2])
    except ValueError:
        return None
    
    if month < 1 or month > DAYS_IN_MONTH_COUNT:
        return None
    
    if day < 1 or day > get_days_in_month(month, year):
        return None
    
    return (day, month, year)


def validate_amount(amount: float) -> bool:
    return amount > 0


def income_handler(amount: float, income_date: str) -> str:
    date_tuple = extract_date(income_date)
    if date_tuple is None:
        return INCORRECT_DATE_MSG
    
    if not validate_amount(amount):
        return NONPOSITIVE_VALUE_MSG
    
    financial_transactions_storage.append({
        "type": "income",
        "amount": amount,
        "date": date_tuple
    })
    return OP_SUCCESS_MSG


def validate_category(category_name: str) -> bool:
    if '::' not in category_name:
        return False
    
    common, target = category_name.split('::', 1)
    
    if common in EXPENSE_CATEGORIES:
        return target in EXPENSE_CATEGORIES[common]
    
    return False


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    date_tuple = extract_date(income_date)
    if date_tuple is None:
        return INCORRECT_DATE_MSG
    
    if not validate_amount(amount):
        return NONPOSITIVE_VALUE_MSG
    
    if not validate_category(category_name):
        return NOT_EXISTS_CATEGORY
    
    financial_transactions_storage.append({
        "type": "expense",
        "category": category_name,
        "amount": amount,
        "date": date_tuple
    })
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    categories = []
    for common, targets in EXPENSE_CATEGORIES.items():
        categories.extend(f"{common}::{target}" for target in targets)
    return "\n".join(sorted(categories))


def stats_handler(report_date: str) -> str:
    date_tuple = extract_date(report_date)
    if date_tuple is None:
        return INCORRECT_DATE_MSG
    
    day, month, year = date_tuple
    
    total_capital = 0.0
    monthly_income = 0.0
    monthly_expenses = 0.0
    expenses_by_category: dict[str, float] = {}
    
    for transaction in financial_transactions_storage:
        trans_day, trans_month, trans_year = transaction["date"]
        
        # Расчет капитала (все операции до указанной даты)
        if (trans_year < year or 
            (trans_year == year and trans_month < month) or 
            (trans_year == year and trans_month == month and trans_day <= day)):
            if transaction["type"] == "income":
                total_capital += transaction["amount"]
            else:
                total_capital -= transaction["amount"]
        
        # Статистика за месяц (только текущий месяц до указанной даты)
        if trans_year == year and trans_month == month and trans_day <= day:
            if transaction["type"] == "income":
                monthly_income += transaction["amount"]
            elif transaction["type"] == "expense":
                monthly_expenses += transaction["amount"]
                category = transaction.get("category", "")
                if "::" in category:
                    target_category = category.split("::")[1]
                else:
                    target_category = category
                expenses_by_category[target_category] = expenses_by_category.get(target_category, 0) + transaction["amount"]
    
    profit_loss = monthly_income - monthly_expenses
    
    result = [f"Your statistics as of {report_date}:"]
    result.append(f"Total capital: {total_capital:.2f} rubles")
    
    if profit_loss >= 0:
        result.append(f"This month, the profit amounted to {profit_loss:.2f} rubles.")
    else:
        result.append(f"This month, the loss amounted to {abs(profit_loss):.2f} rubles.")
    
    result.append(f"Income: {monthly_income:.2f} rubles")
    result.append(f"Expenses: {monthly_expenses:.2f} rubles")
    
    if expenses_by_category:
        result.append("Details (category: amount):")
        sorted_categories = sorted(expenses_by_category.items())
        for i, (category, amount) in enumerate(sorted_categories, 1):
            result.append(f"{i}. {category}: {amount:.0f}")
    else:
        result.append("Details (category: amount):")
    
    return "\n".join(result)


def process_income(parts: list[str]) -> None:
    """Обработка команды income"""
    if len(parts) != INCOME_ARGS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return
    
    amount_str = parts[1]
    date_str = parts[2]
    
    amount_str = amount_str.replace(',', '.')
    try:
        amount = float(amount_str)
    except ValueError:
        print(UNKNOWN_COMMAND_MSG)
        return
    
    result = income_handler(amount, date_str)
    print(result)


def process_cost(parts: list[str]) -> None:
    """Обработка команды cost"""
    if len(parts) == COST_CATEGORIES_ARGS_COUNT and parts[1] == "categories":
        print(cost_categories_handler())
    elif len(parts) == COST_FULL_ARGS_COUNT:
        category_name = parts[1]
        amount_str = parts[2]
        date_str = parts[3]
        
        amount_str = amount_str.replace(',', '.')
        try:
            amount = float(amount_str)
        except ValueError:
            print(UNKNOWN_COMMAND_MSG)
            return
        
        result = cost_handler(category_name, amount, date_str)
        print(result)
    else:
        print(UNKNOWN_COMMAND_MSG)


def process_stats(parts: list[str]) -> None:
    """Обработка команды stats"""
    if len(parts) != STATS_ARGS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return
    
    date_str = parts[1]
    print(stats_handler(date_str))


def main() -> None:
    """Главная функция для обработки команд"""
    while True:
        try:
            command_line = input().strip()
            
            if not command_line:
                continue
            
            parts = command_line.split()
            command = parts[0].lower()
            
            if command == "exit":
                break
            elif command == "income":
                process_income(parts)
            elif command == "cost":
                process_cost(parts)
            elif command == "stats":
                process_stats(parts)
            else:
                print(UNKNOWN_COMMAND_MSG)
        
        except EOFError:
            break


if __name__ == "__main__":
    main()
