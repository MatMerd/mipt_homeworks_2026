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
    "Other": ("SomeCategory", "SomeOtherCategory"),
}

financial_transactions_storage: list[dict[str, Any]] = []


def add_error_stub() -> None:
    financial_transactions_storage.append({})


def is_leap_year(year: int) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0


def extract_date(raw: str) -> tuple[int, int, int] | None:
    parts = raw.split("-")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        return None

    day, month, year = (int(part) for part in parts)
    if month < 1 or month > 12 or year < 0:
        return None

    month_days = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
    if month == 2 and is_leap_year(year):
        return (day, month, year) if 1 <= day <= 29 else None
    return (day, month, year) if 1 <= day <= month_days[month] else None


def valid_date(raw: str) -> bool:
    return extract_date(raw) is not None


def parse_amount(raw_amount: str) -> float | None:
    amount = raw_amount.replace(",", ".")
    if not amount:
        return None
    body = amount[1:] if amount[0] in "+-" else amount
    if not body or body == "." or body.count(".") > 1:
        return None
    if not all(ch.isdigit() or ch == "." for ch in body):
        return None
    return float(amount)


def parse_category(category_name: str) -> tuple[str, str] | None:
    parts = category_name.split("::")
    if len(parts) != 2:
        return None
    return parts[0], parts[1]


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        add_error_stub()
        return NONPOSITIVE_VALUE_MSG

    parsed_date = extract_date(income_date)
    if parsed_date is None:
        add_error_stub()
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({"operation_type": "income", "amount": amount, "date": parsed_date})
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if amount <= 0:
        add_error_stub()
        return NONPOSITIVE_VALUE_MSG

    parsed_date = extract_date(income_date)
    if parsed_date is None:
        add_error_stub()
        return INCORRECT_DATE_MSG

    parsed_category = parse_category(category_name)
    if parsed_category is None:
        add_error_stub()
        return NOT_EXISTS_CATEGORY
    common_category, target_category = parsed_category
    if common_category not in EXPENSE_CATEGORIES or target_category not in EXPENSE_CATEGORIES[common_category]:
        add_error_stub()
        return NOT_EXISTS_CATEGORY

    financial_transactions_storage.append(
        {"operation_type": "cost", "category": category_name, "amount": amount, "date": parsed_date}
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    rows: list[str] = []
    for common_category, target_categories in EXPENSE_CATEGORIES.items():
        for target_category in target_categories:
            rows.append(f"{common_category}::{target_category}")
    return "\n".join(rows)


def is_date_before(date: str, target_date: str) -> bool:
    parsed_date = extract_date(date)
    parsed_target_date = extract_date(target_date)
    if parsed_date is None or parsed_target_date is None:
        return False
    day1, month1, year1 = parsed_date
    day2, month2, year2 = parsed_target_date
    return (year1, month1, day1) <= (year2, month2, day2)


def count_stats_for_date(report_date: str) -> tuple[float, float, dict[str, float]]:
    parsed_report_date = extract_date(report_date)
    if parsed_report_date is None:
        return 0.0, 0.0, {}

    report_month, report_year = parsed_report_date[1], parsed_report_date[2]
    costs_amount = 0.0
    incomes_amount = 0.0
    categories: dict[str, float] = {}

    for record in financial_transactions_storage:
        if not record:
            continue

        raw_date = record.get("date")
        if isinstance(raw_date, tuple):
            current_date = raw_date
        elif isinstance(raw_date, str):
            current_date = extract_date(raw_date)
        else:
            current_date = None
        if current_date is None:
            continue

        day, month, year = current_date
        current_date_as_str = f"{day:02d}-{month:02d}-{year:04d}"
        if not is_date_before(current_date_as_str, report_date):
            continue
        if month != report_month or year != report_year:
            continue

        raw_amount = record.get("amount")
        amount = float(raw_amount) if isinstance(raw_amount, (int, float)) else 0.0
        is_cost = record.get("operation_type") == "cost" or (
            record.get("operation_type") is None and "category" in record
        )
        if is_cost:
            costs_amount += amount
            raw_category = record.get("category")
            if isinstance(raw_category, str) and raw_category:
                categories[raw_category] = categories.get(raw_category, 0.0) + amount
        else:
            incomes_amount += amount

    costs_amount = round(costs_amount, 2)
    incomes_amount = round(incomes_amount, 2)
    for category, amount in categories.items():
        categories[category] = round(amount, 2)
    return costs_amount, incomes_amount, categories


def form_stats_answer(report_date: str, stats: tuple[float, float, dict[str, float]]) -> str:
    costs_amount, incomes_amount, categories = stats
    total_capital = round(costs_amount - incomes_amount, 2)
    amount_word = "loss" if total_capital < 0 else "profit"

    category_rows = []
    for index, (category, amount) in enumerate(categories.items()):
        category_rows.append(f"{index}. {category}: {amount}")

    return f"""Your statistics as of {report_date}:
Total capital: {total_capital} rubles
This month, the {amount_word} amounted to {total_capital} rubles.
Income: {costs_amount} rubles
Expenses: {incomes_amount} rubles

Details (category: amount):
{"\n".join(category_rows)}
"""


def stats_handler(report_date: str) -> str:
    if not valid_date(report_date):
        return INCORRECT_DATE_MSG
    return form_stats_answer(report_date, count_stats_for_date(report_date))


def process_command(*args: str) -> None:
    if not args:
        print(UNKNOWN_COMMAND_MSG)
        return

    if args[0] == "income" and len(args) == 3:
        amount = parse_amount(args[1])
        if amount is None:
            print(UNKNOWN_COMMAND_MSG)
        else:
            print(income_handler(amount, args[2]))
        return

    if args[0] == "cost":
        if len(args) == 2 and args[1] == "categories":
            print(cost_categories_handler())
            return
        if len(args) == 4:
            amount = parse_amount(args[2])
            if amount is None:
                print(UNKNOWN_COMMAND_MSG)
            else:
                print(cost_handler(args[1], amount, args[3]))
            return

    if args[0] == "stats" and len(args) == 2:
        print(stats_handler(args[1]))
        return

    print(UNKNOWN_COMMAND_MSG)


def string_to_float(string: str) -> float:
    return float(string.replace(",", "."))


def main() -> None:
    request = input()
    while request:
        process_command(*request.split())
        request = input()


if __name__ == "__main__":
    main()
