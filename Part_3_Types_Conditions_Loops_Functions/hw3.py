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
EXPECTED_CATEGORY_PARTS = 2
expenses_by_category = "expenses_by_category"
TYPE_KEY = "type"
AMOUNT_KEY = "amount"
DATE_KEY = "date_str"
CATEGORY_KEY = "category"

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
    return all(not (char < "0" or char > "9") for char in s)


def _has_valid_decimal_separator(s: str, i: int) -> bool:
    return i != 0 and i != len(s) - 1


def _is_valid_number(s: str) -> bool:
    if not s:
        return False

    decimal_sep_count = 0
    for _i, char in enumerate(s):
        if char in (",", "."):
            decimal_sep_count += 1
            if decimal_sep_count > 1:
                return False
        elif not char.isdigit():
            return False

    return True


def _validate_date_parts(parts: list[str]) -> tuple[int, int, int] | None:
    if len(parts) != DATE_PARTS_COUNT:
        return None

    for part in parts:
        if not _is_digit_string(part):
            return None

    day_val = int(parts[0])
    month_val = int(parts[1])
    year_val = int(parts[2])
    return (day_val, month_val, year_val)


def _validate_date_values(day: int, month: int, year: int) -> bool:
    if month < MIN_MONTH or month > MAX_MONTH:
        return False
    days_in_month = _get_days_in_month(month, year)
    return not (day < MIN_DAY or day > days_in_month)


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    parts = maybe_dt.split("-")
    date_parts = _validate_date_parts(parts)
    if date_parts is None:
        return None

    day_val, month_val, year_val = date_parts
    if not _validate_date_values(day_val, month_val, year_val):
        return None
    return date_parts


def convert_amount(amount_str: str) -> float | None:
    if not _is_valid_number(amount_str):
        return None
    normalized = amount_str.replace(",", ".")
    return float(normalized)


def parse_date_to_str(date_tuple: tuple[int, int, int]) -> str:
    day_str = f"{date_tuple[0]:02d}"
    month_str = f"{date_tuple[1]:02d}"
    year_str = f"{date_tuple[2]:04d}"
    return f"{day_str}-{month_str}-{year_str}"


def compare_dates(
    date1: tuple[int, int, int],
    date2: tuple[int, int, int],
) -> int:
    if date1[2] != date2[2]:
        return -1 if date1[2] < date2[2] else 1
    if date1[1] != date2[1]:
        return -1 if date1[1] < date2[1] else 1
    if date1[0] != date2[0]:
        return -1 if date1[0] < date2[0] else 1
    return 0


def is_same_month(
    date1: tuple[int, int, int],
    date2: tuple[int, int, int],
) -> bool:
    months_equal = date1[1] == date2[1]
    years_equal = date1[2] == date2[2]
    return months_equal and years_equal


def income_handler(amount: float, income_date: str) -> None:
    financial_transactions_storage.append(
        {
            TYPE_KEY: "income",
            AMOUNT_KEY: amount,
            DATE_KEY: income_date,
        }
    )
    print(OP_SUCCESS_MSG)


def income_validate(description: tuple[str]) -> None:
    if len(description) != EXPECTED_INCOME_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount = convert_amount(description[0])
    if amount is None:
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
            TYPE_KEY: "cost",
            CATEGORY_KEY: category_name,
            AMOUNT_KEY: amount,
            DATE_KEY: cost_date,
        }
    )
    print(OP_SUCCESS_MSG)


def validate_category(category_str: str) -> tuple[str, str] | None:
    if len(category_str.split("::")) != EXPECTED_CATEGORY_PARTS:
        return None

    common_category, target_cat = category_str.split("::")

    category_exists = False
    for cat_name, targets in EXPENSE_CATEGORIES:
        if cat_name == common_category and target_cat in targets:
            category_exists = True
            break

    if not category_exists:
        return None

    return (common_category, target_cat)


def print_available_categories() -> None:
    for common_cat, targets in EXPENSE_CATEGORIES:
        for target in targets:
            print(f"{common_cat}::{target}")


def _validate_cost_amount(amount_str: str) -> float | None:
    amount = convert_amount(amount_str)
    if amount is None or amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return None
    return amount


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

    amount = _validate_cost_amount(description[1])
    if amount is None:
        return

    date_tuple = extract_date(description[2])
    if date_tuple is None:
        print(INCORRECT_DATE_MSG)
        return

    cost_handler(
        f"{category[0]}::{category[1]}",
        amount,
        parse_date_to_str(date_tuple),
    )


def _process_income_transaction(
    transaction: dict,
    target_date: tuple,
    total: float,
    month_inc: float,
) -> tuple[float, float]:
    total += transaction[AMOUNT_KEY]
    trans_date = extract_date(transaction[DATE_KEY])
    if trans_date is not None and is_same_month(trans_date, target_date):
        month_inc += transaction[AMOUNT_KEY]
    return total, month_inc


def _process_cost_transaction(
    transaction: dict,
    target_date: tuple,
    total: float,
    month_exp: float,
    expenses: dict,
) -> tuple[float, float, dict]:
    total -= transaction[AMOUNT_KEY]
    trans_date = extract_date(transaction[DATE_KEY])
    if trans_date is not None and is_same_month(trans_date, target_date):
        month_exp += transaction[AMOUNT_KEY]
        category = transaction[CATEGORY_KEY]
        expenses[category] = expenses.get(category, 0) + transaction[AMOUNT_KEY]
    return total, month_exp, expenses


def _initialize_statistics() -> dict:
    return {
        "tatal": 0,
        "month_income": 0,
        "month_expenses": 0,
        expenses_by_category: {}
    }


def _process_transaction(
        transaction: dict,
        stats: dict,
        target_date: tuple
) -> None:
    trans_date = extract_date(transaction[DATE_KEY])
    if trans_date is None:
        return

    if compare_dates(trans_date, target_date) > 0:
        return

    if transaction[TYPE_KEY] == "income":
        stats["total"] += transaction[AMOUNT_KEY]
        if is_same_month(trans_date, target_date):
            stats["month_income"] += transaction[AMOUNT_KEY]
    else:
        stats["total"] -= transaction[AMOUNT_KEY]
        if is_same_month(trans_date, target_date):
            stats["month_expenses"] += transaction[AMOUNT_KEY]
            category = transaction[CATEGORY_KEY]
            stats[expenses_by_category][category] = (
                    stats[expenses_by_category].get(category, 0) + transaction[AMOUNT_KEY]
            )


def calculate_statistics(
        date_str: str,
) -> tuple[float, float, float, dict[str, float]] | None:
    target_date = extract_date(date_str)
    if target_date is None:
        return None

    stats = _initialize_statistics()

    for transaction in financial_transactions_storage:
        _process_transaction(transaction, stats, target_date)

    return stats["tatal"], stats["month_income"], stats["month_expenses"], stats[expenses_by_category]


def _get_category_sort_key(item: tuple[str, float]) -> str:
    return item[0].lower()


def _format_amount(amount: float) -> str:
    return f"{amount:.2f}".replace(".", ",")


def _print_statistics_header(report_date: str) -> None:
    print(f"Your statistics as of {report_date}:")


def _print_capital_and_profit(
    total_capital: float,
    profit_loss: float,
    month_income: float,
    month_expenses: float,
) -> None:
    print(f"Total capital: {_format_amount(total_capital)} rubles")
    if profit_loss >= 0:
        print(
            f"This month, the profit amounted to {_format_amount(profit_loss)} rubles."
        )
    else:
        loss = abs(profit_loss)
        print(f"This month, the loss amounted to {_format_amount(loss)} rubles.")
    print(f"Income: {_format_amount(month_income)} rubles")
    print(f"Expenses: {_format_amount(month_expenses)} rubles")


def _print_expenses_details(expenses_by_category: dict[str, float]) -> None:
    print("\nDetails (category: amount):")
    if expenses_by_category:
        sorted_categories = sorted(
            expenses_by_category.items(),
            key=_get_category_sort_key,
        )
        for idx, (category, amount) in enumerate(sorted_categories, 1):
            print(f"{idx}. {category}: {_format_amount(amount)}")
    else:
        print()


def stats_handler(report_date: str) -> None:
    result = calculate_statistics(report_date)
    if result is None:
        return

    total_capital, month_income, month_expenses, expenses_by_category = result

    _print_statistics_header(report_date)
    _print_capital_and_profit(
        total_capital,
        month_income - month_expenses,
        month_income,
        month_expenses,
    )
    _print_expenses_details(expenses_by_category)


def stats_validator(description: tuple[str]) -> None:
    if len(description) != EXPECTED_STATS_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return

    date_tuple = extract_date(description[0])
    if date_tuple is None:
        print(INCORRECT_DATE_MSG)
        return

    stats_handler(description[0])


def process_input(line: str) -> None:
    user_input = line.strip()
    if not user_input:
        return

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


def main() -> None:
    line = input()
    while line != "":
        process_input(line)
        line = input()


if __name__ == "__main__":
    main()
