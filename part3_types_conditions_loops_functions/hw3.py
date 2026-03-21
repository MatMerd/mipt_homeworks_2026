#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"
COST_ARGS = 4
INCOME_ARGS = 3
MONTHS = 12
STATS_ARGS = 2

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


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    parts = maybe_dt.split("-")
    if len(parts) != INCOME_ARGS:
        return None

    if not all(p.isdigit() for p in parts):
        return None

    day, month, year = map(int, parts)
    if month < 1 or month > MONTHS:
        return None

    days_in_month = [31, 28, 31, 30, 31, 30,
                     31, 31, 30, 31, 30, 31]
    if is_leap_year(year):
        days_in_month[1] = 29

    if day < 1 or day > days_in_month[month - 1]:
        return None
    return day, month, year


def date_leq(d1: tuple[int, int, int], d2: tuple[int, int, int]) -> bool:
    return (d1[2], d1[1], d1[0]) <= (d2[2], d2[1], d2[0])


def income_handler(amount: float, income_date: str) -> str:
    dt = extract_date(income_date)
    if dt is None:
        return INCORRECT_DATE_MSG

    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    financial_transactions_storage.append({"type": "income", "amount": amount, "date": dt})
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if category_name not in EXPENSE_CATEGORIES:
        return NOT_EXISTS_CATEGORY

    dt = extract_date(income_date)
    if dt is None:
        return INCORRECT_DATE_MSG

    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    financial_transactions_storage.append({"type": "cost", "category": category_name, "amount": amount, "date": dt})

    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    lines = []
    for cat, subs in EXPENSE_CATEGORIES.items():
        if subs:
            lines.append(f"{cat}: {', '.join(subs)}")
        else:
            lines.append(cat)
    return "\n".join(lines)


def stats_handler(report_date: str) -> str:
    dt = extract_date(report_date)
    if dt is None:
        return INCORRECT_DATE_MSG

    total_income = 0.0
    total_cost = 0.0
    month_income = 0.0
    month_cost = 0.0
    category_map: dict[str, float] = {}
    t_day, t_month, t_year = dt
    for tr in financial_transactions_storage:
        d = tr["date"]
        if date_leq(d, dt):
            if tr["type"] == "income":
                total_income += tr["amount"]
                if d[1] == t_month and d[2] == t_year:
                    month_income += tr["amount"]
            else:
                total_cost += tr["amount"]
                if d[1] == t_month and d[2] == t_year:
                    month_cost += tr["amount"]
                    cat = tr["category"]
                    category_map[cat] = category_map.get(cat, 0.0) + tr["amount"]

    capital = total_income - total_cost
    diff = month_income - month_cost
    result = []
    result.append(f"Stats as of {t_day:02d}-{t_month:02d}-{t_year}:")
    result.append(f"Total capital: {capital:.2f}")
    if diff >= 0:
        result.append(f"Profit this month: {diff:.2f}")
    else:
        result.append(f"Loss this month: {abs(diff):.2f}")

    result.append(f"Income: {month_income:.2f}")
    result.append(f"Costs: {month_cost:.2f}")
    result.append("Breakdown:")
    for i, cat in enumerate(sorted(category_map), 1):
        result.append(f"{i}. {cat}: {category_map[cat]}")
    return "\n".join(result)


def handle_command(parts: list[str]) -> str:
    command = parts[0]
    result = UNKNOWN_COMMAND_MSG
    if command == "income":
        if len(parts) == INCOME_ARGS:
            try:
                amount = float(parts[1].replace(",", "."))
                result = income_handler(amount, parts[2])
            except ValueError:
                pass

    elif command == "cost":
        if len(parts) == COST_ARGS:
            try:
                amount = float(parts[2].replace(",", "."))
                result = cost_handler(parts[1], amount, parts[3])
            except ValueError:
                pass

    elif command == "stats":
        if len(parts) == STATS_ARGS:
            result = stats_handler(parts[1])

    elif command == "categories":
        result = cost_categories_handler()
    return result


def main() -> None:
    while True:
        try:
            line = input().strip()
        except EOFError:
            break

        if not line:
            continue

        parts = line.split()
        result = handle_command(parts)
        print(result)


if __name__ == "__main__":
    main()
