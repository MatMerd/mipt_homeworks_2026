#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"


# Словарь категорий
EXPENSE_CATEGORIES = {
    "Food": ("FastFood", "Grocery", "Restaurant"),
    "Rent": ("Apartment", "Office"),
    "Gifts": ("Birthday", "NewYear"),
    "Subscriptions": ("Netflix", "Spotify", "Gym"),
    "Transport": ("Taxi", "Bus", "Gas")
}


financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    #Для заданного года определяет: високосный (True) или невисокосный (False).
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def get_days_in_month(month: int, year: int) -> int:
    #Возвращает количество дней в месяце
    if month == 2:
        return 29 if is_leap_year(year) else 28
    elif month in [4, 6, 9, 11]:
        return 30
    else:
        return 31


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    # Парсит дату формата DD-MM-YYYY из строки
    parts = maybe_dt.split('-')
    if len(parts) != 3:
        return None
    
    # Проверка, что все части — цифры
    if not (parts[0].isdigit() and parts[1].isdigit() and parts[2].isdigit()):
        return None
    
    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2])
    
    if month < 1 or month > 12:
        return None
    
    max_days = get_days_in_month(month, year)
    if day < 1 or day > max_days:
        return None
        
    return (day, month, year)


def _parse_amount_input(amount_str: str) -> float | None:
    # Парсинг строки в float, заменяя запятую на точку
    clean = amount_str.replace(',', '.')
    if not clean:
        return None
        
    check_str = clean.lstrip('-')
    if '.' in check_str:
        parts = check_str.split('.')
        if len(parts) > 2:
            return None
        if not parts[0].isdigit() or not parts[1].isdigit():
            return None
    else:
        if not check_str.isdigit():
            return None
            
    return float(clean)


def income_handler(amount: float, income_date: str) -> str:
    # Обработчик дохода
    # Проверка суммы
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG
    
    # Проверка даты
    date_tuple = extract_date(income_date)
    if date_tuple is None:
        return INCORRECT_DATE_MSG
    
    # Сохранение
    financial_transactions_storage.append({
        'amount': amount,
        'date': date_tuple
    })
    
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    """
    Обработчик расхода.
    """
    # Проверка категории
    parts = category_name.split(':')
    parts = [p for p in parts if p] # убираем пустые если были
    
    valid_target_cat = None
    
    if len(parts) >= 2:
        common = parts[0]
        target = parts[1]
        if common in EXPENSE_CATEGORIES and target in EXPENSE_CATEGORIES[common]:
            valid_target_cat = target
    elif category_name in EXPENSE_CATEGORIES:
        valid_target_cat = category_name 
        
    if valid_target_cat is None:
        return NOT_EXISTS_CATEGORY
    
    # Проверка суммы
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG
    
    # Проверка даты
    date_tuple = extract_date(income_date)
    if date_tuple is None:
        return INCORRECT_DATE_MSG
    
    # Сохранение
    financial_transactions_storage.append({
        'category': valid_target_cat,
        'amount': amount,
        'date': date_tuple
    })
    
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    """Возвращает список категорий строкой"""
    result_list = []
    for common, targets in EXPENSE_CATEGORIES.items():
        for target in targets:
            result_list.append(f"{common}::{target}")
    return "\n".join(result_list)


def stats_handler(report_date: str) -> str:
    # Вывод статистики.
    target_date_tuple = extract_date(report_date)
    if target_date_tuple is None:
        return INCORRECT_DATE_MSG
    
    target_day, target_month, target_year = target_date_tuple
    target_comparable = (target_year, target_month, target_day)
    
    total_income = 0.0
    total_expense = 0.0
    
    # Считаем общий капитал
    for trans in financial_transactions_storage:
        d, m, y = trans['date']
        trans_comparable = (y, m, d)
        
        if trans_comparable < target_comparable:
            if 'category' in trans: # Это расход
                total_expense += trans['amount']
            else: # Это доход
                total_income += trans['amount']
    
    total_capital = total_income - total_expense
    
    # Считаем статистику за текущий меся
    month_income = 0.0
    month_expense = 0.0
    expenses_by_cat = {}
    
    for trans in financial_transactions_storage:
        d, m, y = trans['date']
        
        # Проверяем, что транзакция в том же месяце что и запрошенная дата
        if y == target_year and m == target_month:
            if 'category' in trans:
                month_expense += trans['amount']
                cat = trans['category']
                if cat not in expenses_by_cat:
                    expenses_by_cat[cat] = 0.0
                expenses_by_cat[cat] += trans['amount']
            else:
                month_income += trans['amount']
    
    # Формируем вывод
    amount_word = "loss" if total_capital < 0 else "profit"
    
    # Формируем список категории
    sorted_cats = sorted(expenses_by_cat.keys())
    cat_lines = []
    for i, cat in enumerate(sorted_cats, 1):
        amount = expenses_by_cat[cat]
        if amount == int(amount):
            cat_lines.append(f"{i}. {cat}: {int(amount)}")
        else:
            cat_lines.append(f"{i}. {cat}: {str(amount).replace('.', ',')}")
    
    category_details_stat = "\n".join(cat_lines)
    
    # Формируем итоговую строку
    res = f"""Your statistics as of {report_date}:
Total capital: {total_capital:.2f} rubles
This month, the {amount_word} amounted to {abs(total_capital):.2f} rubles.
Income: {month_income:.2f} rubles
Expenses: {month_expense:.2f} rubles

Details (category: amount):
{category_details_stat}"""

    return res


def main() -> None:
    """Основной цикл программы"""
    while True:
        try:
            line = input()
        except EOFError:
            break
            
        parts = line.split()
        if not parts:
            continue
            
        cmd = parts[0]
        args = parts[1:]
        
        if cmd == "income":
            if len(args) != 2:
                print(UNKNOWN_COMMAND_MSG)
                continue
                
            amount_str, date_str = args
            
            # Парсим сумму вручную перед вызовом хендлера
            amount_val = _parse_amount_input(amount_str)
            if amount_val is None:
                print(income_handler(0.0, date_str)) 
            else:
                print(income_handler(amount_val, date_str))
                
        elif cmd == "cost":
            if args and args[0] == "categories":
                print(cost_categories_handler())
                continue
                
            if len(args) != 3:
                print(UNKNOWN_COMMAND_MSG)
                continue
                
            category_name, amount_str, date_str = args
            
            amount_val = _parse_amount_input(amount_str)
            if amount_val is None:
                print(cost_handler(category_name, 0.0, date_str))
            else:
                print(cost_handler(category_name, amount_val, date_str))
                
        elif cmd == "stats":
            if len(args) != 1:
                print(UNKNOWN_COMMAND_MSG)
                continue
            print(stats_handler(args[0]))
        else:
            print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()
