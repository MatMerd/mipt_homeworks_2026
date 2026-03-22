#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

DATE_LIST_LENGHT = 3
MONTHS_NUMBER = 12
FEBRUARY_NUMBER = 2
ALLOWED_SYMBOLS = "0123456789.-"
CATEGORY_PARTS_COUNT = 2
INCOME_QUERY_LENGTH = 3
COST_CATEGORIES_QUERY_LENGTH = 2
COST_QUERY_LENGTH = 4
STATS_QUERY_LENGTH = 2

DAYS_IN_MONTH = (
    31, 28, 31, 30, 31, 30,
    31, 31, 30, 31, 30, 31
)

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
    if year % 4 == 0 and year % 100 != 0:
        return True
    return year % 400 == 0


def get_days_in_month(month: int, year: int) -> int:
    if month == FEBRUARY_NUMBER:
        if (is_leap_year(year)):
            return 29
        return 28
    return DAYS_IN_MONTH[month - 1]


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    list_of_mabe_dt = maybe_dt.split("-")
    if len(list_of_mabe_dt) != DATE_LIST_LENGHT:
        return None

    if any(not date_fragment.isdigit() for date_fragment in list_of_mabe_dt):
        return None

    day = int(list_of_mabe_dt[0])
    month = int(list_of_mabe_dt[1])
    year = int(list_of_mabe_dt[2])

    if not (1 <= month <= MONTHS_NUMBER and year > 0):
        return None

    max_days = get_days_in_month(month, year)
    if not (1 <= day <= max_days):
        return None

    return day, month, year


def extract_amount(maybe_amount: str) -> float | None:
    maybe_amount = maybe_amount.replace(",", ".")

    if maybe_amount.startswith("-"):
        if maybe_amount.count("-") > 1:
            return None
        amount_str = maybe_amount[1:]
    else:
        amount_str = maybe_amount

    if amount_str.count(".") > 1:
        return None

    for symbol in amount_str:
        if symbol not in "0123456789.":
            return None

    amount = float(maybe_amount)

    if amount <= 0:
        return -1

    return amount


def validate_category(name_of_category: str) -> bool:
    category_parts = name_of_category.split("::")
    if len(category_parts) != CATEGORY_PARTS_COUNT:
        return False

    common_category, target_category = category_parts
    return common_category in EXPENSE_CATEGORIES and target_category in EXPENSE_CATEGORIES[common_category]


def get_target_category(category_name: str) -> str:
    return category_name.split("::", maxsplit=1)[1]


def save_transaction() -> None:
    financial_transactions_storage.append({})


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        save_transaction()
        return NONPOSITIVE_VALUE_MSG

    date = extract_date(income_date)
    if date is None:
        save_transaction()
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({"amount": amount, "date": date})
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if not validate_category(category_name):
        save_transaction()
        return NOT_EXISTS_CATEGORY

    if amount <= 0:
        save_transaction()
        return NONPOSITIVE_VALUE_MSG

    date = extract_date(income_date)
    if date is None:
        save_transaction()
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({"category": category_name, "amount": amount, "date": date})
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return "\n".join([
        f"{common_category}::{target_category}"
        for common_category, subcategories in EXPENSE_CATEGORIES.items()
        for target_category in subcategories
    ])


def is_same_month(date1: tuple[int, int, int], date2: tuple[int, int, int]) -> bool:
    return date1[1] == date2[1] and date1[2] == date2[2]


def is_date_before_or_equal(date1: tuple[int, int, int], date2: tuple[int, int, int]) -> bool:
    for i in range(2, -1, -1):
        if date2[i] != date1[i]:
            return date1[i] < date2[i]
    return True


def calculate_month_stats(date: tuple[int, int, int]) -> tuple[float, float, dict[str, float]]:
    """Calculate month income, expenses and details."""
    month_income = 0
    month_expenses = 0
    details_by_category: dict[str, float] = {}
    
    for transaction in financial_transactions_storage:
        if not transaction:
            continue
            
        transaction_date = transaction["date"]
        if not is_date_before_or_equal(date, transaction_date):
            continue
            
        amount = transaction["amount"]
        if "category" in transaction:
            if is_same_month(transaction_date, date):
                month_expenses += amount
                target_category = get_target_category(transaction["category"])
                if target_category in details_by_category:
                    details_by_category[target_category] += amount
                else:
                    details_by_category[target_category] = amount
        else:
            if is_same_month(transaction_date, date):
                month_income += amount
    
    return month_income, month_expenses, details_by_category


def calculate_total_capital() -> float:
    total_capital = 0
    
    for transaction in financial_transactions_storage:
        if not transaction:
            continue
            
        amount = transaction["amount"]
        if "category" in transaction:
            total_capital -= amount
        else:
            total_capital += amount
    
    return total_capital


def format_statistics(report_date: str, total: float, income: float, expenses: float, details: dict[str, float]) -> str:
    result_amount = abs(income - expenses)
    result_type = "loss" if income - expenses < 0 else "profit"
    
    statistics = [
        f"Your statistics as of {report_date}:",
        f"Total capital: {total:.2f} rubles",
        f"This month, the {result_type} amounted to {result_amount:.2f} rubles.",
        f"Income: {income:.2f} rubles",
        f"Expenses: {expenses:.2f} rubles",
        "",
        "Details (category: amount):",
    ]
    
    sorted_categories = sorted(details.items(), key=lambda item: item[0].lower())
    for idx, (category_name, amount) in enumerate(sorted_categories, start=1):
        statistics.append(f"{idx}. {category_name}: {amount:.2f}")
    
    return "\n".join(statistics)


def stats_handler(report_date: str) -> str:
    date = extract_date(report_date)
    if date is None:
        return INCORRECT_DATE_MSG
    
    total_capital = calculate_total_capital()
    month_income, month_expenses, details_by_category = calculate_month_stats(date)
    
    return format_statistics(report_date, total_capital, month_income, month_expenses, details_by_category)


def output_handler(result: str) -> None:
    print(result)
    if result == NOT_EXISTS_CATEGORY:
        categories_info = cost_categories_handler()
        if categories_info:
            print(categories_info)


def handle_income_command(input_parts: list[str]) -> None:
    if len(input_parts) != INCOME_QUERY_LENGTH:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount = extract_amount(input_parts[1])
    if amount is None:
        print(UNKNOWN_COMMAND_MSG)
        return

    print(income_handler(amount, input_parts[2]))


def handle_cost(input_parts: list[str]) -> None:
    if len(input_parts) == COST_CATEGORIES_QUERY_LENGTH and input_parts[1] == "categories":
        print(cost_categories_handler())
        return

    if len(input_parts) != COST_QUERY_LENGTH:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount = extract_amount(input_parts[2])
    if amount is None:
        print(UNKNOWN_COMMAND_MSG)
        return

    output_handler(cost_handler(input_parts[1], amount, input_parts[3]))


def handle_stats_command(input_parts: list[str]) -> None:
    if len(input_parts) != STATS_QUERY_LENGTH:
        print(UNKNOWN_COMMAND_MSG)
        return

    print(stats_handler(input_parts[1]))


def dispatch_command() -> bool:
    input_line = input().strip()
    if not input_line:
        return False

    input_parts = input_line.split()
    command_name = input_parts[0]

    if command_name == "income":
        handle_income_command(input_parts)
    elif command_name == "cost":
        handle_cost(input_parts)
    elif command_name == "stats":
        handle_stats_command(input_parts)
    else:
        print(UNKNOWN_COMMAND_MSG)

    return True


def main() -> None:
    while dispatch_command():
        pass


if __name__ == "__main__":
    main()
