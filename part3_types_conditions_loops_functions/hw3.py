#!/usr/bin/env python
from __future__ import annotations
from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

COUNT_OF_DATE_PARTS = 3
DAYS_IN_LONG_MONTH = 31
DAYS_IN_SHORT_MONTH = 30
DAYS_IN_LEAP_FEBRUARY = 29
DAYS_IN_COMMON_FEBRUARY = 28
FEBRUARY = 2
LONG_MONTHS = (1, 3, 5, 7, 8, 10, 12)
SHORT_MONTHS = (4, 6, 9, 11)

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
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def parse_date(maybe_dt: str) -> tuple[int, int, int] | None:
    parts = maybe_dt.split('-')
    if len(parts) != COUNT_OF_DATE_PARTS:
        return None
    int_parts = []
    for val in parts:
        if not val.isdigit():
            return None
        int_parts.append(int(val))
    return int_parts[0], int_parts[1], int_parts[2]

def count_of_days_in_month(month: int, year: int) -> int | None:
    if month in SHORT_MONTHS:
        return DAYS_IN_SHORT_MONTH
    if month in LONG_MONTHS:
        return DAYS_IN_LONG_MONTH
    if month == FEBRUARY:
        return DAYS_IN_LEAP_FEBRUARY if is_leap_year(year) else DAYS_IN_COMMON_FEBRUARY
    return None

def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    parsed = parse_date(maybe_dt)
    if parsed is None:
        return None
    d, m, y = parsed
    if y < 1 or m < 1 or m > 12 or d < 1:
        return None
    max_d = count_of_days_in_month(m, y)
    if max_d is None or d > max_d:
        return None
    return d, m, y

def parse_amount(amount_str: str) -> float | None:
    try:
        return float(amount_str.replace(',', '.'))
    except ValueError:
        return None

def is_valid_category(category_name: str) -> bool:
    if "::" not in category_name:
        return False
    parts = category_name.split("::")
    if len(parts) != 2:
        return False
    main_cat, sub_cat = parts
    if main_cat in EXPENSE_CATEGORIES:
        if sub_cat in EXPENSE_CATEGORIES[main_cat] or (main_cat == "Other" and not sub_cat):
            return True
    return False

def income_handler(amount: float, income_date: tuple[int, int, int]) -> str:
    financial_transactions_storage.append({
        "type": "income",
        "amount": amount,
        "date": income_date
    })
    return OP_SUCCESS_MSG

def cost_handler(category_name: str, amount: float, cost_date: tuple[int, int, int]) -> str:
    financial_transactions_storage.append({
        "type": "cost",
        "category": category_name,
        "amount": amount,
        "date": cost_date
    })
    return OP_SUCCESS_MSG

def cost_categories_handler() -> str:
    lines = []
    for main_cat, subs in EXPENSE_CATEGORIES.items():
        if subs:
            lines.append(f"- {main_cat}: {', '.join(subs)}")
        else:
            lines.append(f"- {main_cat}")
    return "\n".join(lines)

def stats_handler(report_date_str: str) -> str:
    dt = extract_date(report_date_str)
    if dt is None: return INCORRECT_DATE_MSG
    d_rep, m_rep, y_rep = dt

    total_capital = 0.0
    month_income = 0.0
    month_expenses = 0.0
    expenses_by_cat = {}

    for item in financial_transactions_storage:
        d, m, y = item["date"]
        if (y < y_rep) or (y == y_rep and m < m_rep) or (y == y_rep and m == m_rep and d <= d_rep):
            if item["type"] == "income":
                total_capital += item["amount"]
            else:
                total_capital -= item["amount"]
        
        if y == y_rep and m == m_rep and d <= d_rep:
            if item["type"] == "income":
                month_income += item["amount"]
            else:
                month_expenses += item["amount"]
                cat = item["category"].split("::")[1]
                expenses_by_cat[cat] = expenses_by_cat.get(cat, 0.0) + item["amount"]

    diff = month_income - month_expenses
    type_str = "profit" if diff >= 0 else "loss"
    
    res = [
        f"Your statistics as of {report_date_str}:",
        f"Total capital: {total_capital:.2f} rubles",
        f"This month, the {type_str} amounted to {abs(diff):.2f} rubles.",
        f"Income: {month_income:.2f} rubles",
        f"Expenses: {month_expenses:.2f} rubles",
        "",
        "Details (category: amount):"
    ]
    
    if month_expenses > 0:
        sorted_cats = sorted(expenses_by_cat.items())
        for i, (name, val) in enumerate(sorted_cats, 1):
            if val % 1 == 0:
                val_str = str(int(val))
            else:
                val_str = f"{val:.2f}"
            res.append(f"{i}. {name}: {val_str}")
            
    return "\n".join(res)

def main() -> None:
    print("--- Программа запущена! Вводите команды: ---")
    while True:
        try:
            line = input().strip()
        except EOFError:
            break
        if not line: continue
        
        parts = line.split()
        cmd = parts[0]

        if cmd == "income":
            if len(parts) != 3:
                print(UNKNOWN_COMMAND_MSG)
                continue
            
            amount = parse_amount(parts[1])
            date_dt = extract_date(parts[2])
            
            if amount is None:
                print(UNKNOWN_COMMAND_MSG)
            elif amount <= 0:
                print(NONPOSITIVE_VALUE_MSG)
            elif date_dt is None:
                print(INCORRECT_DATE_MSG)
            else:
                print(income_handler(amount, date_dt))

        elif cmd == "cost":
            if len(parts) == 2 and parts[1] == "categories":
                print(cost_categories_handler())
                continue
            
            if len(parts) != 4:
                print(UNKNOWN_COMMAND_MSG)
                continue

            cat, amount_str, date_str = parts[1], parts[2], parts[3]
            amount = parse_amount(amount_str)
            date_dt = extract_date(date_str)

            if amount is None:
                print(UNKNOWN_COMMAND_MSG)
            elif amount <= 0:
                print(NONPOSITIVE_VALUE_MSG)
            elif date_dt is None:
                print(INCORRECT_DATE_MSG)
            elif not is_valid_category(cat):
                print(NOT_EXISTS_CATEGORY)
                print(cost_categories_handler())
            else:
                print(cost_handler(cat, amount, date_dt))

        elif cmd == "stats":
            if len(parts) != 2:
                print(UNKNOWN_COMMAND_MSG)
            else:
                print(stats_handler(parts[1]))
        else:
            print(UNKNOWN_COMMAND_MSG)

if __name__ == "__main__":
    main()