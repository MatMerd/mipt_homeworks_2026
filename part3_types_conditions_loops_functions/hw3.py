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

financial_transactions_storage: list[Any] = []

# constants
DAYS_IN_MONTH = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
MONTHS_IN_YEAR = 12
DAYS_IN_LEAP_FEBRUARY = 29
FEBRUARY_NUMBER = 2
DATE_COUNT_PARTS = 3

INCOME_PARTS_COUNT = 3
COST_PARTS_COUNT = 4
STATS_PARTS_COUNT = 2
COST_CATEGORIES_PARTS_COUNT = 2

KEY_AMOUNT = "amount"
KEY_DATE = "date"
KEY_CATEGORY = "category"
YEAR_MULTIPLIER = 10000
MONTH_MULTIPLIER = 100


def is_leap_year(year: int) -> bool:
    divisible_by_4 = year % 4 == 0
    if not divisible_by_4:
        return False
    divisible_by_100 = year % 100 == 0
    if not divisible_by_100:
        return True
    return year % 400 == 0


def get_days_in_month(year: int, month: int) -> int:
    if month == FEBRUARY_NUMBER and is_leap_year(year):
        return DAYS_IN_LEAP_FEBRUARY
    return DAYS_IN_MONTH[month - 1]


def is_valid_month(month: int) -> bool:
    return 1 <= month <= MONTHS_IN_YEAR


def all_digits(parts: list[str]) -> bool:
    return all(part.isdigit() for part in parts)


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    date_parts = maybe_dt.split("-")
    if len(date_parts) != DATE_COUNT_PARTS:
        return None
    if not all_digits(date_parts):
        return None
    day = int(date_parts[0])
    month = int(date_parts[1])
    year = int(date_parts[2])
    if day < 1 or month < 1 or year < 1:
        return None
    if is_valid_month(month) and day <= get_days_in_month(year, month):
        return (day, month, year)
    return None


def is_valid_number(s: str) -> bool:
    if not s:
        return False
    start = 0
    if s[0] == "-":
        start = 1
    normalized = s[start:].replace(",", ".")
    if not normalized:
        return False
    dot_count = 0
    for ch in normalized:
        if ch == ".":
            dot_count += 1
            if dot_count > 1:
                return False
        if not ch.isdigit():
            return False
    return True


def parse_amount(amount_str: str) -> float | None:
    if not is_valid_number(amount_str):
        return None
    return float(amount_str.replace(",", "."))


def validate_category(category_str: str) -> tuple[str, str] | None:
    if "::" not in category_str:
        return None
    common, target = category_str.split("::", 1)
    if common not in EXPENSE_CATEGORIES:
        return None
    if target not in EXPENSE_CATEGORIES[common]:
        return None
    return (common, target)


def format_categories() -> str:
    return "\n".join(
        f"{common}::{target}"
        for common, targets in EXPENSE_CATEGORIES.items()
        for target in targets
    )


def convert_date_to_int(date: tuple[int, int, int]) -> int:
    year_part = date[2] * YEAR_MULTIPLIER
    month_part = date[1] * MONTH_MULTIPLIER
    return (year_part + month_part) + date[0]


def is_date_in_month(date: tuple[int, int, int], year: int, month: int) -> bool:
    return date[1] == month and date[2] == year


def _should_include_record(record: dict, target_int: int) -> bool:
    record_date = record.get(KEY_DATE)
    if not record_date:
        return False
    return convert_date_to_int(record_date) <= target_int


def _calculate_total_capital_until(target_date: tuple[int, int, int]) -> float:
    target_int = convert_date_to_int(target_date)
    total = 0
    for record in financial_transactions_storage:
        if not isinstance(record, dict):
            continue
        if not _should_include_record(record, target_int):
            continue
        amount = record.get(KEY_AMOUNT, 0)
        if KEY_CATEGORY in record:
            total -= amount
        else:
            total += amount
    return total


def _process_record_for_month(
    record: dict, year: int, month: int
) -> tuple[float, float, dict[str, float]]:
    record_date = record.get(KEY_DATE)
    if not record_date:
        return 0, 0, {}
    if not is_date_in_month(record_date, year, month):
        return 0, 0, {}
    amount = record.get(KEY_AMOUNT, 0)
    if KEY_CATEGORY in record:
        cat = record.get(KEY_CATEGORY, "")
        return 0, amount, {cat: amount}
    return amount, 0, {}


def _get_month_amounts_and_categories(
    year: int, month: int
) -> tuple[float, float, dict[str, float]]:
    total_income: float = 0
    total_expenses: float = 0
    categories: dict[str, float] = {}
    for record in financial_transactions_storage:
        if not isinstance(record, dict):
            continue
        inc, exp, cat_dict = _process_record_for_month(record, year, month)
        total_income += inc
        total_expenses += exp
        for cat, amt in cat_dict.items():
            categories[cat] = categories.get(cat, 0) + amt
    return total_income, total_expenses, categories


def _calculate_month_income_expenses(
    target_date: tuple[int, int, int]
) -> tuple[float, float, dict[str, float]]:
    return _get_month_amounts_and_categories(target_date[2], target_date[1])


def _format_details(categories: dict[str, float]) -> list[str]:
    if not categories:
        return [""]
    lines = []
    sorted_cats = sorted(categories.items())
    for idx, (cat, amt) in enumerate(sorted_cats, start=1):
        amt_str = f"{int(amt)}" if amt == int(amt) else f"{amt:.2f}"
        lines.append(f"{idx}. {cat}: {amt_str}")
    return lines


def _format_statistics(
    report_date: str,
    total_capital: float,
    month_income: float,
    month_expenses: float,
    categories: dict[str, float],
) -> str:
    profit = month_income - month_expenses
    profit_word = "profit" if profit > 0 else "loss"
    profit_abs = abs(profit)
    lines = [
        f"Your statistics as of {report_date}:",
        f"Total capital: {total_capital:.2f} rubles",
        f"This month, the {profit_word} amounted to {profit_abs:.2f} rubles.",
        f"Income: {month_income:.2f} rubles",
        f"Expenses: {month_expenses:.2f} rubles",
        "",
        "Details (category: amount):",
    ]
    lines.extend(_format_details(categories))
    return "\n".join(lines)


def income_handler(amount: float, income_date: str) -> str:
    date_tuple = extract_date(income_date)
    if amount <= 0:
        financial_transactions_storage.append(None)
        return NONPOSITIVE_VALUE_MSG
    if date_tuple is None:
        financial_transactions_storage.append(None)
        return INCORRECT_DATE_MSG
    financial_transactions_storage.append({KEY_AMOUNT: amount, KEY_DATE: date_tuple})
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    date_tuple = extract_date(income_date)
    if amount <= 0:
        financial_transactions_storage.append(None)
        return NONPOSITIVE_VALUE_MSG
    if date_tuple is None:
        financial_transactions_storage.append(None)
        return INCORRECT_DATE_MSG
    if validate_category(category_name) is None:
        financial_transactions_storage.append(None)
        return NOT_EXISTS_CATEGORY
    financial_transactions_storage.append(
        {KEY_CATEGORY: category_name, KEY_AMOUNT: amount, KEY_DATE: date_tuple}
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return format_categories()


def stats_handler(report_date: str) -> str:
    target_date = extract_date(report_date)
    if target_date is None:
        return INCORRECT_DATE_MSG
    total_capital = _calculate_total_capital_until(target_date)
    month_income, month_expenses, categories = _calculate_month_income_expenses(
        target_date
    )
    return _format_statistics(
        report_date, total_capital, month_income, month_expenses, categories
    )


def _handle_income_command(command_parts: list[str]) -> None:
    if len(command_parts) != INCOME_PARTS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return
    amount_val = parse_amount(command_parts[1])
    if amount_val is None:
        print(UNKNOWN_COMMAND_MSG)
        return
    result = income_handler(amount_val, command_parts[2])
    print(result)


def _handle_cost_command(command_parts: list[str]) -> None:
    if len(command_parts) == COST_CATEGORIES_PARTS_COUNT and command_parts[1] == "categories":
        print(cost_categories_handler())
        return
    if len(command_parts) != COST_PARTS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return
    amount_val = parse_amount(command_parts[2])
    if amount_val is None:
        print(UNKNOWN_COMMAND_MSG)
        return
    result = cost_handler(command_parts[1], amount_val, command_parts[3])
    print(result)


def _handle_stats_command(command_parts: list[str]) -> None:
    if len(command_parts) != STATS_PARTS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return
    result = stats_handler(command_parts[1])
    print(result)


def _handle_line(line: str) -> None:
    parts = line.split()
    if not parts:
        return
    cmd = parts[0]
    if cmd == "income":
        _handle_income_command(parts)
    elif cmd == "cost":
        _handle_cost_command(parts)
    elif cmd == "stats":
        _handle_stats_command(parts)
    else:
        print(UNKNOWN_COMMAND_MSG)


def _read_input() -> str | None:
    try:
        return input()
    except EOFError:
        return None


def main() -> None:
    while True:
        line = _read_input()
        if line is None or not line:
            break
        _handle_line(line)


if __name__ == "__main__":
    main()
