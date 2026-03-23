#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

Date = tuple[int, int, int]

incomes: list[tuple[float, Date]] = []
expenses: list[tuple[str, float, Date]] = []
financial_transactions_storage: list[dict[str, object]] = []

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

valid_days_in_month: list[int] = [
    0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31
]


def is_leap_year(year: int) -> bool:
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0


def validate_category(category_str: str) -> tuple[str, str] | None:
    if "::" not in category_str or not category_str:
        return None

    parent, sub = category_str.split("::", 1)

    if not parent or not sub or " " in parent or " " in sub:
        return None
    if parent not in EXPENSE_CATEGORIES:
        return None
    if sub not in EXPENSE_CATEGORIES[parent]:
        return None

    return parent, sub


def extract_date(maybe_dt: str) -> Date | None:
    parts = maybe_dt.split("-")
    if len(parts) != DATE_SPLIT_LENGTH:
        return None

    day, month, year = parts
    if not (day.isdigit() and month.isdigit() and year.isdigit()):
        return None

    return int(day), int(month), int(year)


def valid_date(date: Date | None) -> bool:
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


def parse_amount(amount: str) -> float | None:
    amount = amount.replace(",", ".")
    if amount.count(".") > 1:
        return None

    if not all(c.isdigit() or c == "." for c in amount):
        return None

    return float(amount)


def valid_amount(amount: float | None) -> bool:
    return amount is not None and amount > 0


def get_all_categories() -> str:
    categories: list[str] = []
    for parent, subs in EXPENSE_CATEGORIES.items():
        categories.extend([f"{parent}::{sub}" for sub in subs])
    return "\n".join(categories)


def is_before_or_on(trans_date: Date, target_date: Date) -> bool:
    if trans_date[2] != target_date[2]:
        return trans_date[2] < target_date[2]
    if trans_date[1] != target_date[1]:
        return trans_date[1] < target_date[1]
    return trans_date[0] <= target_date[0]


def is_same_month_year(date1: Date, date2: Date) -> bool:
    return date1[1] == date2[1] and date1[2] == date2[2]


def calculate_income(target: Date) -> tuple[float, float]:
    capital: float = 0
    month_income: float = 0

    for amount, date in incomes:
        if is_before_or_on(date, target):
            capital += amount
            if is_same_month_year(date, target):
                month_income += amount

    return capital, month_income


def calculate_expenses(target: Date) -> tuple[float, float, dict[str, float]]:
    capital: float = 0
    month_expenses: float = 0
    categories: dict[str, float] = {}

    for category, amount, date in expenses:
        if is_before_or_on(date, target):
            capital -= amount
            if is_same_month_year(date, target):
                month_expenses += amount
                categories[category] = categories.get(category, 0.0) + amount

    return capital, month_expenses, categories


def process_transactions(target_date: Date) -> tuple[float, float, float, dict[str, float]]:
    inc_capital, month_income = calculate_income(target_date)
    exp_capital, month_expenses, categories = calculate_expenses(target_date)
    return inc_capital + exp_capital, month_income, month_expenses, categories


def make_up_statistics(date: Date) -> tuple[float, float, float, dict[str, float]]:
    return process_transactions(date)


def print_stats(stats: tuple[float, float, float, dict[str, float]], date: str) -> None:
    capital, income, expenses_total, categories = stats

    print(f"Your statistics as of {date}:")
    print(f"Total capital: {capital:.2f} rubles")

    delta = income - expenses_total
    if delta > 0:
        print(f"This month, the profit amounted to {delta:.2f} rubles.")
    else:
        delta *= -1;
        print(f"This month, the loss amounted to {delta:.2f} rubles.")

    print(f"Income: {income:.2f} rubles")
    print(f"Expenses: {expenses_total:.2f} rubles\n")
    print("Details (category: amount):")

    for idx, (cat, amt) in enumerate(sorted(categories.items()), 1):
        print(f"{idx}. {cat}: {int(amt):,}")


def income_handler(amount: str | float, income_date: str) -> str:
    amount_parsed = parse_amount(str(amount))
    date = extract_date(income_date)

    if not valid_amount(amount_parsed):
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    if not valid_date(date):
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    if amount_parsed is None or date is None:
        financial_transactions_storage.append({})
        return UNKNOWN_COMMAND_MSG

    incomes.append((amount_parsed, date))
    financial_transactions_storage.append({
        "amount": amount_parsed,
        "date": date
    })

    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: str | float, income_date: str) -> str:
    category_parts = validate_category(category_name)
    amount_parsed = parse_amount(str(amount))
    date = extract_date(income_date)

    if not valid_amount(amount_parsed):
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    if not valid_date(date):
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    if category_parts is None:
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY

    if amount_parsed is None or date is None:
        financial_transactions_storage.append({})
        return UNKNOWN_COMMAND_MSG

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

    if date is None:
        financial_transactions_storage.append({})
        return UNKNOWN_COMMAND_MSG

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
    lines.append(f"Expenses: {expenses_total:.2f} rubles\n")
    lines.append("Details (category: amount):")

    for cat, amt in sorted(categories.items()):
        lines.append(f"{cat}: {int(amt)}")

    return "\n".join(lines)


def handle_income(command_split: list[str]) -> None:
    if len(command_split) != INCOME_ARGS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return

    print(income_handler(command_split[1], command_split[2]))


def handle_cost(command_split: list[str]) -> None:
    if len(command_split) == COST_ARGS_COUNT and command_split[1] == "categories":
        print(cost_categories_handler())
        return

    if len(command_split) != COST_ARGS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return

    print(cost_handler(command_split[1], command_split[2], command_split[3]))


def handle_stats(command_split: list[str]) -> None:
    if len(command_split) != STATS_ARGS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return

    print(stats_handler(command_split[1]))


def main() -> None:
    command_split = input().split()

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
