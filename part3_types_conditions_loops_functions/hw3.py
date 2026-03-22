#!/usr/bin/env python

from typing import Any

ALLOWED_AMOUNT_SYMBOLS = "0123456789.,"

AMOUNT_KEY = "amount"
DATE_KEY = "date"
MAIN_CAT_KEY = "main"
SUB_CAT_KEY = "sub"

DATE_LEN = 10
DATE_FRAGMENTS = 3

DAY_INDEX = 0
MONTH_INDEX = 1
YEAR_INDEX = 2

MONTHS_NUMBER = 12
FEBRUARY_NUMBER = 2
FEBRUARY_DAYS_COUNT = 29

MONTH_DAYS = (
    31, 28, 31, 30, 31, 30,
    31, 31, 30, 31, 30, 31
)

INCOME_ARGS = 3
COST_ARGS = 4
STATS_ARGS = 2

CMD_INCOME = "income"
CMD_COST = "cost"
CMD_STATS = "stats"
CMD_CATEGORIES = "categories"

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


IncomeDict = dict[str, Any]
ExpenseDict = dict[str, Any]
financial_transactions_storage: list[dict[str, Any]] = []
incomes: list[IncomeDict] = []
expenses: list[ExpenseDict] = []



def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    if year % 4 != 0 and year > 0:
        return False
    elif year % 100 != 0:
        return True
    return year % 400 == 0

def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    if len(maybe_dt) != DATE_LEN:
        return None
    if maybe_dt[2] != "-" or maybe_dt[5] != "-":
        return None

    d, m, y = maybe_dt[:2], maybe_dt[3:5], maybe_dt[6:]

    if not (d.isdigit() and m.isdigit() and y.isdigit()):
        return None

    day, month, year = int(d), int(m), int(y)

    if not (1 <= month <= MONTHS_NUMBER):
        return None

    feb = FEBRUARY_DAYS_COUNT if is_leap_year(year) else 28
    month_days = list(MONTH_DAYS)
    month_days[FEBRUARY_NUMBER - 1] = feb

    if not (1 <= day <= month_days[month - 1]):
        return None

    return day, month, year

def date_leq(d1: tuple[int, int, int], d2: tuple[int, int, int]) -> bool:
    return (d1[YEAR_INDEX], d1[MONTH_INDEX], d1[DAY_INDEX]) <= \
           (d2[YEAR_INDEX], d2[MONTH_INDEX], d2[DAY_INDEX])

def is_valid_category(cat: str) -> bool:
    if "::" not in cat:
        return False
    main, sub = cat.split("::", 1)
    return main in EXPENSE_CATEGORIES and sub in EXPENSE_CATEGORIES[main]

def all_categories_str() -> str:
    lines = []
    for main, subs in EXPENSE_CATEGORIES.items():
        for sub in subs:
            lines.append(f"{main}::{sub}")
    return "\n".join(lines)

def parse_amount(amount_str: str) -> float:
    return float(amount_str.replace(",", "."))




def income_handler(amount: float, income_date: str) -> str:
    dt = extract_date(income_date)

    if dt is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    financial_transactions_storage.append({
        AMOUNT_KEY: amount,
        DATE_KEY: dt,
    })

    incomes.append({
        AMOUNT_KEY: amount,
        DATE_KEY: dt
    })

    return OP_SUCCESS_MSG

def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if not is_valid_category(category_name):
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY

    dt = extract_date(income_date)

    if dt is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    financial_transactions_storage.append({
        "category": category_name,
        AMOUNT_KEY: amount,
        DATE_KEY: dt,
    })

    main, sub = category_name.split("::", 1)

    expenses.append({
        MAIN_CAT_KEY: main,
        SUB_CAT_KEY: sub,
        AMOUNT_KEY: amount,
        DATE_KEY: dt
    })

    return OP_SUCCESS_MSG

def cost_categories_handler() -> str:
    return all_categories_str()

def stats_handler(report_date: str) -> str:
    dt = extract_date(report_date)
    if dt is None:
        return INCORRECT_DATE_MSG

    day_r, month_r, year_r = dt

    total_capital = 0.0
    month_income = 0.0
    month_expenses = 0.0
    cats: dict[str, float] = {}

    for inc in incomes:
        if date_leq(inc[DATE_KEY], dt):
            total_capital += inc[AMOUNT_KEY]
        if inc[DATE_KEY][MONTH_INDEX] == month_r and inc[DATE_KEY][YEAR_INDEX] == year_r:
            month_income += inc[AMOUNT_KEY]

    for exp in expenses:
        if date_leq(exp[DATE_KEY], dt):
            total_capital -= exp[AMOUNT_KEY]
        if exp[DATE_KEY][MONTH_INDEX] == month_r and exp[DATE_KEY][YEAR_INDEX] == year_r:
            month_expenses += exp[AMOUNT_KEY]
            cats[exp[SUB_CAT_KEY]] = cats.get(exp[SUB_CAT_KEY], 0.0) + exp[AMOUNT_KEY]

    month_result = month_income - month_expenses

    print(f"Your statistics as of {report_date}:")
    print(f"Total capital: {total_capital} rubles")
    if month_result < 0:
        print(f"This month, the loss amounted to {abs(month_result)} rubles")
    else:
        print(f"This month, the profit amounted to {month_result} rubles")
    print(f"Income: {month_income} rubles")
    print(f"Expenses: {month_expenses} rubles")
    print()
    print("Details (category: amount):")

    for idx, name in enumerate(sorted(cats.keys()), start=1):
        print(f"{idx}. {name}: {cats[name]}")
    return f"Statistic for {report_date}"

def process_income(parts: list[str]) -> None:
    if len(parts) != INCOME_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount = parse_amount(parts[1])
    if amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return

    print(income_handler(amount, parts[2]))

def process_cost(parts: list[str]) -> None:
    if len(parts) == 2 and parts[1] == CMD_CATEGORIES:
        print(all_categories_str())
        return

    if len(parts) != COST_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return

    category, amount_str, date_str = parts[1], parts[2], parts[3]

    if not is_valid_category(category):
        print(NOT_EXISTS_CATEGORY)
        print(all_categories_str())
        return

    amount = parse_amount(amount_str)
    if amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return

    print(cost_handler(category, amount, date_str))

def process_stats(parts: list[str]) -> None:
    if len(parts) != STATS_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return

    date_str = parts[1]
    if extract_date(date_str) is None:
        print(INCORRECT_DATE_MSG)
        return

    stats_handler(date_str)

def dispatch_command(parts: list[str]) -> None:
    cmd = parts[0]

    if cmd == CMD_INCOME:
        process_income(parts)
    elif cmd == CMD_COST:
        process_cost(parts)
    elif cmd == CMD_STATS:
        process_stats(parts)
    else:
        print(UNKNOWN_COMMAND_MSG)

def main() -> None:
    global incomes, expenses

    incomes = []
    expenses = []

    while True:
        try:
            line = input().strip()
        except EOFError:
            break

        if not line:
            continue

        parts = line.split()
        dispatch_command(parts)


if __name__ == "__main__":
    main()
