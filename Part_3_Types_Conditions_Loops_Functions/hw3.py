#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"
EXPECTED_INCOME_ARGS = 2
EXPECTED_COST_ARGS = 3
EXPECTED_STATS_ARGS = 1
DATE_PARTS_COUNT = 3
MIN_MONTH = 1
MAX_MONTH = 12
MIN_DAY = 1

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


def is_leap_year(year: int) -> bool:
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0


def _get_days_in_month(month: int, year: int) -> int:
    days = [
        31,
        29 if is_leap_year(year) else 28,
        31,
        30,
        31,
        30,
        31,
        31,
        30,
        31,
        30,
        31,
    ]
    return days[month - 1]


def _is_digit_string(s: str) -> bool:
    if not s:
        return False
    for char in s:
        if char < "0" or char > "9":
            return False
    return True


def _validate_date_parts(parts: list[str]) -> tuple[int, int, int] | None:
    if len(parts) != DATE_PARTS_COUNT:
        return None

    for part in parts:
        if not _is_digit_string(part):
            return None

    return (int(parts[0]), int(parts[1]), int(parts[2]))


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    parts = maybe_dt.split("-")

    date_parts = _validate_date_parts(parts)
    if date_parts is None:
        return None

    day, month, year = date_parts

    if month < MIN_MONTH or month > MAX_MONTH:
        return None

    days_in_month = _get_days_in_month(month, year)
    if day < MIN_DAY or day > days_in_month:
        return None

    return date_parts


def convert_amount(amount_str: str) -> float:
    return float(amount_str.replace(",", "."))


def parse_date_to_str(date_tuple: tuple[int, int, int]) -> str:
    return f"{date_tuple[0]:02d}-{date_tuple[1]:02d}-{date_tuple[2]:04d}"


def compare_dates(date1: tuple[int, int, int], date2: tuple[int, int, int]) -> int:
    if date1[2] != date2[2]:
        return -1 if date1[2] < date2[2] else 1
    if date1[1] != date2[1]:
        return -1 if date1[1] < date2[1] else 1
    if date1[0] != date2[0]:
        return -1 if date1[0] < date2[0] else 1
    return 0


def is_same_month(date1: tuple[int, int, int], date2: tuple[int, int, int]) -> bool:
    return date1[1] == date2[1] and date1[2] == date2[2]


def income_handler(amount: float, income_date: str) -> None:
    financial_transactions_storage.append(
        {"type": "income", "amount": amount, "date_str": income_date}
    )
    print(OP_SUCCESS_MSG)


def income_validate(description: tuple[str]) -> None:
    if len(description) != EXPECTED_INCOME_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return

    try:
        amount = convert_amount(description[0])
    except ValueError:
        print(NONPOSITIVE_VALUE_MSG)
        return

    if amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return

    date_tuple = extract_date(description[1])
    if date_tuple is None:
        print(INCORRECT_DATE_MSG)
        return

    income_handler(amount, parse_date_to_str(date_tuple))


def cost_handler(category_name: str, amount: float, cost_date: str) -> None:
    financial_transactions_storage.append(
        {
            "type": "cost",
            "category": category_name,
            "amount": amount,
            "date_str": cost_date,
        }
    )
    print(OP_SUCCESS_MSG)


def validate_category(category_str: str) -> tuple[str, str] | None:
    if "::" not in category_str:
        return None

    parts = category_str.split("::")
    if len(parts) != 2:
        return None

    common_cat, target_cat = parts[0], parts[1]

    if common_cat not in EXPENSE_CATEGORIES:
        return None

    if target_cat not in EXPENSE_CATEGORIES[common_cat]:
        return None

    return (common_cat, target_cat)


def print_available_categories() -> None:
    for common_cat, targets in EXPENSE_CATEGORIES.items():
        for target in targets:
            print(f"{common_cat}::{target}")


def cost_validator(description: tuple[str]) -> None:
    if len(description) == 1 and description[0] == "categories":
        print_available_categories()
        return

    if len(description) != EXPECTED_COST_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return

    category = validate_category(description[0])
    if category is None:
        print(NOT_EXISTS_CATEGORY)
        print_available_categories()
        return

    try:
        amount = convert_amount(description[1])
    except ValueError:
        print(NONPOSITIVE_VALUE_MSG)
        return

    if amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return

    date_tuple = extract_date(description[2])
    if date_tuple is None:
        print(INCORRECT_DATE_MSG)
        return

    cost_handler(f"{category[0]}::{category[1]}", amount, parse_date_to_str(date_tuple))


def calculate_statistics(
    date_str: str,
) -> tuple[float, float, float, dict[str, float]] | None:
    target_date = extract_date(date_str)
    if target_date is None:
        return None

    total_capital = 0.0
    month_income = 0.0
    month_expenses = 0.0
    expenses_by_category = {}

    for transaction in financial_transactions_storage:
        trans_date = extract_date(transaction["date_str"])
        if trans_date is None:
            continue

        if compare_dates(trans_date, target_date) <= 0:
            if transaction["type"] == "income":
                total_capital += transaction["amount"]
                if is_same_month(trans_date, target_date):
                    month_income += transaction["amount"]
            else:
                total_capital -= transaction["amount"]
                if is_same_month(trans_date, target_date):
                    month_expenses += transaction["amount"]
                    category = transaction["category"]
                    expenses_by_category[category] = (
                        expenses_by_category.get(category, 0) + transaction["amount"]
                    )

    return total_capital, month_income, month_expenses, expenses_by_category


def stats_handler(report_date: str) -> None:
    result = calculate_statistics(report_date)
    if result is None:
        return

    total_capital, month_income, month_expenses, expenses_by_category = result

    sorted_categories = sorted(expenses_by_category.items(), key=lambda x: x[0].lower())

    def format_amount(amount):
        return f"{amount:.2f}".replace(".", ",")

    print(f"Your statistics as of {report_date}:")
    print(f"Total capital: {format_amount(total_capital)} rubles")

    profit_loss = month_income - month_expenses
    if profit_loss >= 0:
        print(
            f"This month, the profit amounted to {format_amount(profit_loss)} rubles."
        )
    else:
        print(
            f"This month, the loss amounted to {format_amount(abs(profit_loss))} rubles."
        )

    print(f"Income: {format_amount(month_income)} rubles")
    print(f"Expenses: {format_amount(month_expenses)} rubles")

    print("\nDetails (category: amount):")
    if sorted_categories:
        for idx, (category, amount) in enumerate(sorted_categories, 1):
            print(f"{idx}. {category}: {format_amount(amount)}")
    else:
        print("")


def stats_validator(description: tuple[str]) -> None:
    if len(description) != EXPECTED_STATS_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return

    date_tuple = extract_date(description[0])
    if date_tuple is None:
        print(INCORRECT_DATE_MSG)
        return

    stats_handler(description[0])


def main() -> None:
    while True:
        try:
            user_input = input()
        except EOFError:
            break

        if not user_input.strip():
            continue

        parts = user_input.split()
        command = parts[0]
        description = tuple(parts[1:])

        match command:
            case "income":
                income_validate(description)
            case "cost":
                cost_validator(description)
            case "stats":
                stats_validator(description)
            case _:
                print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()
