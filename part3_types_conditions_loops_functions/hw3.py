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

DATE_PARTS_COUNT = 3
MONTHS_IN_YEAR = 12
INCOME_COMMAND_ARGS_COUNT = 3
COST_CATEGORIES_ARGS_COUNT = 2
COST_COMMAND_ARGS_COUNT = 4
STATS_COMMAND_ARGS_COUNT = 2

TYPE_KEY = "type"
INCOME_TYPE = "income"
COST_TYPE = "cost"
ZERO_AMOUNT = 0

Date = tuple[int, int, int]
MonthCosts = dict[str, float]
OperationInfo = tuple[str, float, Date, str | None]


def parse_amount(raw: str) -> float | None:
    prepared = raw.replace(",", ".")
    if prepared.count(".") > 1:
        return None

    if not prepared or prepared == ".":
        return None

    for char in prepared:
        if not (char.isdigit() or char == "."):
            return None

    return float(prepared)


def parse_category_name(category_name: str) -> tuple[str, str] | None:
    if category_name.count("::") != 1:
        return None

    common_category, direct_category = category_name.split("::")
    if not common_category or not direct_category:
        return None

    if common_category not in EXPENSE_CATEGORIES:
        return None

    if direct_category not in EXPENSE_CATEGORIES[common_category]:
        return None

    return common_category, direct_category


def reverse_date(date: Date) -> Date:
    return date[2], date[1], date[0]


def is_before(lhs_date: Date, rhs_date: Date) -> bool:
    return reverse_date(lhs_date) <= reverse_date(rhs_date)


def is_in_this_month(date: Date, target: Date) -> bool:
    same_year = date[2] == target[2]
    same_month = date[1] == target[1]
    in_day_range = date[0] <= target[0]
    return same_year and same_month and in_day_range


def extract_operation_info(operation: dict[str, Any]) -> OperationInfo | None:
    operation_type = operation.get(TYPE_KEY)
    operation_date = operation.get("date")
    amount = operation.get("amount")
    subcategory = operation.get("subcategory")

    if not (isinstance(operation_type, str) and isinstance(amount, int | float)):
        return None

    if not (
        isinstance(operation_date, tuple)
        and len(operation_date) == DATE_PARTS_COUNT
        and all(isinstance(part, int) for part in operation_date)
    ):
        return None

    if subcategory is not None and not isinstance(subcategory, str):
        return None

    date: Date = operation_date
    return operation_type, float(amount), date, subcategory


def iter_valid_operations() -> list[OperationInfo]:
    valid_operations: list[OperationInfo] = []
    for operation in financial_transactions_storage:
        if not operation:
            continue

        operation_info = extract_operation_info(operation)
        if operation_info is not None:
            valid_operations.append(operation_info)

    return valid_operations


def update_month_totals(operation_info: OperationInfo, month_income: float, month_costs: MonthCosts) -> float:
    operation_type, amount, _, subcategory = operation_info
    if operation_type == INCOME_TYPE:
        return month_income + amount

    if operation_type == COST_TYPE and subcategory is not None:
        month_costs[subcategory] = month_costs.get(subcategory, ZERO_AMOUNT) + amount

    return month_income


def count_capital(target_date: Date) -> float:
    total: float = ZERO_AMOUNT

    for operation_type, amount, operation_date, _ in iter_valid_operations():
        if not is_before(operation_date, target_date):
            continue

        if operation_type == INCOME_TYPE:
            total += amount
        elif operation_type == COST_TYPE:
            total -= amount

    return total


def count_stats(target_date: Date) -> tuple[float, MonthCosts]:
    month_income: float = ZERO_AMOUNT
    month_costs: MonthCosts = {}

    for operation_info in iter_valid_operations():
        if not is_in_this_month(operation_info[2], target_date):
            continue

        month_income = update_month_totals(operation_info, month_income, month_costs)

    return month_income, month_costs


def is_leap_year(year: int) -> bool:
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0


def days_in_month(month: int, year: int) -> int:
    all_month_days = [
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
    return all_month_days[month - 1]


def extract_date(maybe_dt: str) -> Date | None:
    parts_of_date = maybe_dt.split("-")
    if len(parts_of_date) != DATE_PARTS_COUNT:
        return None

    if not all(part.isdigit() for part in parts_of_date):
        return None

    day, month, year = map(int, parts_of_date)

    if not (1 <= month <= MONTHS_IN_YEAR):
        return None

    if not (1 <= day <= days_in_month(month, year)):
        return None

    return day, month, year


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    date = extract_date(income_date)
    if date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({TYPE_KEY: INCOME_TYPE, "amount": amount, "date": date})
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    status: str | None = None
    date: Date | None = None
    parsed_category: tuple[str, str] | None = None

    if amount <= 0:
        status = NONPOSITIVE_VALUE_MSG
    else:
        date = extract_date(income_date)
        if date is None:
            status = INCORRECT_DATE_MSG
        else:
            parsed_category = parse_category_name(category_name)
            if parsed_category is None:
                status = NOT_EXISTS_CATEGORY

    if status is not None:
        financial_transactions_storage.append({})
        return status

    if parsed_category is None: # без этой проверки линтер ругается #
        financial_transactions_storage.append({})
        return UNKNOWN_COMMAND_MSG

    _, direct_category = parsed_category
    financial_transactions_storage.append(
        {
            TYPE_KEY: COST_TYPE,
            "category": category_name,
            "subcategory": direct_category,
            "amount": amount,
            "date": date,
        }
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return "\n".join(
        f"{common_category}::{direct_category}"
        for common_category, direct_categories in EXPENSE_CATEGORIES.items()
        for direct_category in direct_categories
    )


def format_stats_lines(report_date: str, capital: float, month_income: float, month_costs: MonthCosts) -> list[str]:
    total_costs = sum(month_costs.values())
    profit = month_income - total_costs

    lines: list[str] = []
    lines.append(f"Your statistics as of {report_date}:")
    lines.append(f"Total capital: {capital:.2f} rubles")

    if profit >= 0:
        lines.append(f"This month, the profit amounted to {profit:.2f} rubles.")
    else:
        lines.append(f"This month, the loss amounted to {abs(profit):.2f} rubles.")

    lines.append(f"Income: {month_income:.2f} rubles")
    lines.append(f"Expenses: {total_costs:.2f} rubles")
    lines.append("")
    lines.append("Details (category: amount):")

    for index, category in enumerate(sorted(month_costs), start=1):
        lines.append(f"{index}. {category}: {int(month_costs[category])}")

    return lines


def stats_handler(report_date: str) -> str:
    date = extract_date(report_date)
    if date is None:
        return INCORRECT_DATE_MSG

    capital = count_capital(date)
    month_income, month_costs = count_stats(date)
    lines = format_stats_lines(report_date, capital, month_income, month_costs)
    return "\n".join(lines)


def handle_income_command(question: list[str]) -> None:
    if len(question) != INCOME_COMMAND_ARGS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount = parse_amount(question[1])
    if amount is None:
        print(UNKNOWN_COMMAND_MSG)
        return

    print(income_handler(amount, question[2]))


def handle_cost_command(question: list[str]) -> None:
    if len(question) == COST_CATEGORIES_ARGS_COUNT and question[1] == "categories":
        print(cost_categories_handler())
        return

    if len(question) != COST_COMMAND_ARGS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount = parse_amount(question[2])
    if amount is None:
        print(UNKNOWN_COMMAND_MSG)
        return

    result = cost_handler(question[1], amount, question[3])
    print(result)
    if result == NOT_EXISTS_CATEGORY:
        print(cost_categories_handler())


def handle_stats_command(question: list[str]) -> None:
    if len(question) != STATS_COMMAND_ARGS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return

    print(stats_handler(question[1]))


def dispatch_command(command: str, question: list[str]) -> bool:
    handlers = {
        "income": handle_income_command,
        "cost": handle_cost_command,
        "stats": handle_stats_command,
    }

    handler = handlers.get(command)
    if handler is None:
        return False

    handler(question)
    return True


def main() -> None:
    is_running = True
    while is_running:
        question = input().strip().split()
        if not question:
            print(UNKNOWN_COMMAND_MSG)
            continue

        command = question[0]
        if not dispatch_command(command, question):
            print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()
