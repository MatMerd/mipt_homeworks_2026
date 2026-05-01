# Глобальный список для хранения всех транзакций (доходы и расходы)
# Тесты будут смотреть сюда, чтобы проверить, добавились ли данные
financial_transactions_storage = []

# Словарь категорий. Ключ - общая, значение - список конкретных
EXPENSE_CATEGORIES = {
    "Food": ["FastFood", "Grocery", "Restaurant"],
    "Rent": ["Apartment", "Office"],
    "Gifts": ["Birthday", "NewYear"],
    "Subscriptions": ["Netflix", "Spotify", "Gym"],
    "Transport": ["Taxi", "Bus", "Gas"]
}

# Константы для сообщений
OP_SUCCESS_MSG = "Added"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"


def is_leap(year):
    # Проверка на високосный год
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def get_days_in_month(month, year):
    # Сколько дней в месяце
    if month == 2:
        return 29 if is_leap(year) else 28
    elif month in [4, 6, 9, 11]:
        return 30
    else:
        return 31


def parse_date(date_str):
    #Парсим дату из строки DD-MM-YYYY
    parts = date_str.split('-')
    if len(parts) != 3:
        return None
    
    # Проверка, что все цифры
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


def parse_amount(amount_str):
    # Парсим сумму
    clean = amount_str.replace(',', '.')
    if not clean:
        return None
        
    # Простая проверка на число
    check_str = clean.lstrip('-')
    if '.' in check_str:
        integer_part, decimal_part = check_str.split('.')
        if not integer_part.isdigit() or not decimal_part.isdigit():
            return None
    else:
        if not check_str.isdigit():
            return None
            
    return float(clean)


def income_handler(amount_str, date_str):
    """
    Обработчик команды income.
    Принимает строки, как из консоли.
    """
    # Проверка числа
    amount = parse_amount(amount_str)
    if amount is None or amount <= 0:
        return NONPOSITIVE_VALUE_MSG
    
    # Проверка даты
    date_tuple = parse_date(date_str)
    if date_tuple is None:
        return INCORRECT_DATE_MSG
    
    # Сохраняем в общее хранилище
    financial_transactions_storage.append({
        'amount': amount,
        'date': date_tuple
    })
    
    return OP_SUCCESS_MSG


def cost_handler(category_name, amount_str, date_str):
    # Обработчик команды cost.
    # Проверка категории
    # Формат может быть Common, Target или просто Common
    parts = category_name.split(':')
    parts = [p for p in parts if p] # убираем пустые если было
    
    valid_target_cat = None
    
    if len(parts) >= 2:
        common = parts[0]
        target = parts[1]
        if common in EXPENSE_CATEGORIES and target in EXPENSE_CATEGORIES[common]:
            valid_target_cat = target
    elif category_name in EXPENSE_CATEGORIES:
        # Если ввели просто общую категорию
        valid_target_cat = category_name 
        
    if valid_target_cat is None:
        return NOT_EXISTS_CATEGORY
    
    # Проверка суммы
    amount = parse_amount(amount_str)
    if amount is None or amount <= 0:
        return NONPOSITIVE_VALUE_MSG
    
    # Проверка даты
    date_tuple = parse_date(date_str)
    if date_tuple is None:
        return INCORRECT_DATE_MSG
    
    # Сохраняем
    financial_transactions_storage.append({
        'category': valid_target_cat,
        'amount': amount,
        'date': date_tuple
    })
    
    return OP_SUCCESS_MSG


def cost_categories_handler():
    # Возвращает список категорий строкой для вывода
    result_list = []
    for common, targets in EXPENSE_CATEGORIES.items():
        for target in targets:
            result_list.append(f"{common}::{target}")
    return "\n".join(result_list)


def stats_handler(date_str):
    # Вывод статистики.
    target_date_tuple = parse_date(date_str)
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
    
    # Считаем статистику за ТЕКУЩИЙ месяц 
    month_income = 0.0
    month_expense = 0.0
    expenses_by_cat = {}
    
    for trans in financial_transactions_storage:
        d, m, y = trans['date']
        
        # Проверяем, что транзакция в том же месяце, что и запрошенная дата
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
    
    # Формируем список категорий
    sorted_cats = sorted(expenses_by_cat.keys())
    cat_lines = []
    for i, cat in enumerate(sorted_cats, 1):
        amount = expenses_by_cat[cat]
        if amount == int(amount):
            cat_lines.append(f"{i}. {cat}: {int(amount)}")
        else:
            cat_lines.append(f"{i}. {cat}: {str(amount).replace('.', ',')}")
    
    category_details_stat = "\n".join(cat_lines)
    
    res = f"""Your statistics as of {date_str
