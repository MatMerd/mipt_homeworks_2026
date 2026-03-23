#!/usr/bin/env python
from typing import List, Tuple, Dict, Optional

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

incomes: List[Tuple[float, Tuple[int, int, int]]] = []
expenses: List[Tuple[str, float, Tuple[int, int, int]]] = []
financial_transactions_storage: List[Dict[str, object]] = []

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

MONTHS_IN_YEAR = 12
DAYS_IN_JANUARY = 31
DAYS_IN_FEBRUARY_NORMAL = 28
DAYS_IN_FEBRUARY_LEAP = 29
DATE_SPLIT_LENGTH = 3
INCOME_ARGS_COUNT = 3
COST_ARGS_COUNT = 4
STATS_ARGS_COUNT = 2
FEBRUARY = 2
COST_CATEGORIES_ARGS_COUNT = 2

Date = Tuple[int, int, int]

valid_days_in_month: List[int] = [
    0,
    DAYS_IN_JANUARY,
    28,
    DAYS_IN_JANUARY,
    30,
    DAYS_IN_JANUARY,
    30,
    DAYS_IN_JANUARY,
    DAYS_IN_JANUARY,
    30,
    DAYS_IN_JANUARY,
    30,
    DAYS_IN_JANUARY,
]


def is_leap_year(year: int) -> bool:
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0


def validate_category(category_str: str) -> Optional[Tuple[str, str]]:
    if "::" not in category_str or not category_str:
        return None

    parent, sub = category_str.split("::", 1)

    if not parent or not sub or " " in parent or " " in sub:
        return None
    if parent not in EXPENSE_CATEGORIES:
        return None
    subs = EXPENSE_CATEGORIES[parent]
    if not subs or sub not in subs:
        return None

    return parent, sub


def extract_date(maybe_dt: str) -> Optional[Date]:
    date = maybe_dt.split("-")

    if len(date) != DATE_SPLIT_LENGTH:
        return None

    day, month, year = date

    if not (day.isdigit() and month.isdigit() and year.isdigit()):
        return None

    return int(day), int(month), int(year)


def valid_date(date: Optional[Date]) -> bool:
    if date is None:
        return False

    day, month, year = date

    if month < 1 or month > MONTHS_IN_YEAR or day < 1 or year < 1:
        return False

    if month == FEBRUARY:
        if is_leap_year(year):
            return day <= DAYS_IN_FEBRUARY_LEAP
        return day <= DAYS_IN_FEBRUARY_NORMAL

    return day <= valid_days_in_month[month]


def parse_amount(amount: str) -> Optional[float]:
    amount = amount.replace(",", ".")

    if amount.count(".") > 1:
        return None

    for char in amount:
        if not (char.isdigit() or char == "."):
            return None

    return float(amount)


def valid_amount(amount: Optional[float]) -> bool:
    if amount is None:
        return False
    return amount > 0


def get_all_categories() -> str:
    categories = []
    for parent, subs in EXPENSE_CATEGORIES.items():
        if subs:
            categories.extend([f"{parent}::{sub}" for sub in subs])
    return "\n".join(categories)


def is_before_or_on(trans_date: Date, target_date: Date) -> bool:
    if trans_date[2] != target_date[2]:
        return trans_date[2] < target_date[2]
    if trans_date[1] != target_date[1]:
        return trans_date[1] < target_date[1]
    return trans_date[0] <= target_date[0]


def is_same_month_year(date1, date2):
    return date1[1] == date2[1] and date1[2] == date2[2]


def calculate_income(target: Date) -> Tuple[float, float]:
    capital = 0
    month_income = 0

    for inc in incomes:
        if is_before_or_on(inc[1], target):
            capital += inc[0]
            if is_same_month_year(inc[1], target):
                month_income += inc[0]

    return capital, month_income


def calculate_expenses(target: Date) -> Tuple[float, float, Dict[str, float]]:
    capital = 0
    month_expenses = 0
    categories = {}

    for exp in expenses:
        if is_before_or_on(exp[2], target):
            capital -= exp[1]
            if is_same_month_year(exp[2], target):
                month_expenses += exp[1]
                cat = exp[0]
                categories[cat] = categories.get(cat, 0) + exp[1]

    return capital, month_expenses, categories


def process_transactions(target_date: Date) -> Tuple[float, float, float, Dict[str, float]]:
    inc_capital, month_income = calculate_income(target_date)
    exp_capital, month_expenses, categories = calculate_expenses(target_date)
    return inc_capital + exp_capital, month_income, month_expenses, categories


def make_up_statistics(date: Date) -> List[object]:
    return list(process_transactions(date))


def print_stats(stats: List[object], date: str) -> None:
    capital, income, expenses_total, categories = stats

    print(f"Your statistics as of {date}:")
    print(f"Total capital: {capital:.2f} rubles")

    if income > expenses_total:
        profit = income - expenses_total
        print(f"This month, the profit amounted to {profit:.2f} rubles.")
    else:
        loss = expenses_total - income
        print(f"This month, the loss amounted to {loss:.2f} rubles.")

    print(f"Income: {income:.2f} rubles")
    print(f"Expenses: {expenses_total:.2f} rubles")
    print()
    print("Details (category: amount):")

    if not categories:
        print()
        return

    for idx, (category, amount) in enumerate(sorted(categories.items()), 1):
        print(f"{idx}. {category}: {int(amount):,}")


def income_handler(amount: str, income_date: str) -> str:
    amount_parsed = parse_amount(str(amount))
    date = extract_date(income_date)

    if not valid_amount(amount_parsed):
        return NONPOSITIVE_VALUE_MSG
    if not valid_date(date):
        return INCORRECT_DATE_MSG

    incomes.append((amount_parsed, date))
    financial_transactions_storage.append({
        "amount": amount_parsed,
        "date": date
    })
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: str, income_date: str) -> str:
    category_parts = validate_category(category_name)
    if category_parts is None:
        error_msg = f"{NOT_EXISTS_CATEGORY}\n{get_all_categories()}"
        return error_msg

    amount_parsed = parse_amount(str(amount))
    if not valid_amount(amount_parsed):
        return NONPOSITIVE_VALUE_MSG

    date = extract_date(income_date)
    if not valid_date(date):
        return INCORRECT_DATE_MSG

    expenses.append((category_name, amount_parsed, date))
    financial_transactions_storage.append({
        "category": category_name,
        "amount": amount_parsed,
        "date": date
    })
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return get_all_categories()


def stats_handler(report_date: str) -> str:
    date = extract_date(report_date)
    if not valid_date(date):
        return INCORRECT_DATE_MSG

    capital, income, expenses_total, categories = make_up_statistics(date)

    lines = [
        f"Your statistics as of {report_date}:",
        f"Total capital: {capital:.2f} rubles",
    ]

    delta = income - expenses_total
    if delta > 0:
        lines.append(f"This month, the profit amounted to {delta:.2f} rubles.")
    else:
        delta *= -1
        lines.append(f"This month, the loss amounted to {delta:.2f} rubles.")

    lines.append(f"Income: {income:.2f} rubles")
    lines.append(f"Expenses: {expenses_total:.2f} rubles")
    lines.append("")
    lines.append("Details (category: amount):")

    if categories:
        for category, amount in sorted(categories.items()):
            lines.append(f"{category}: {int(amount)}")
    else:
        lines.append("")

    return "\n".join(lines)


def handle_income(command_split: List[str]) -> None:
    if len(command_split) != INCOME_ARGS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount_str, date_str = command_split[1:]
    result = income_handler(amount_str, date_str)
    print(result)


def handle_cost(command_split: List[str]) -> None:
    if len(command_split) == COST_CATEGORIES_ARGS_COUNT and command_split[1] == "categories":
        print(cost_categories_handler())
        return

    if len(command_split) != COST_ARGS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return

    category, amount_str, date_str = command_split[1:]
    result = cost_handler(category, amount_str, date_str)
    print(result)


def handle_stats(command_split: List[str]) -> None:
    if len(command_split) != STATS_ARGS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return

    date_str = command_split[1]
    result = stats_handler(date_str)
    print(result)


def main() -> None:
    command = input()
    command_split = command.split(" ")

    if command_split[0] == "income":
        handle_income(command_split)
    elif command_split[0] == "cost":
        handle_cost(command_split)
    elif command_split[0] == "stats":
        handle_stats(command_split)
    else:
        print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()
