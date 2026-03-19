#!/usr/bin/env python
DataTuple = tuple[int, int, int]

income_dict: dict[DataTuple, int] = {}
expense_dict: dict[DataTuple, int] = {}
details_dict: dict[DataTuple, dict[str, int]] = {}

LEN_DATE_LIST = 3
MONTHS_THIRTY_DAYS = (4, 6, 9, 11)
FEBRUARY = 2
MIN_MONTH = 1
MAX_MONTH = 12
MIN_DAY = 1
MAX_DAY_IN_THIRTY_DAYS_MONTH = 30
MAX_DAY_IN_THIRTY_ONE_DAY_MONTH = 31
MAX_DAY_FEB_LEAP = 29
MAX_DAY_FEB_NORMAL = 28
DATE_LENGTH = 10
INCOME_ARGS = 3
COST_ARGS = 4
STATS_ARGS = 2

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"


def income(amount: int, date: str) -> None:
    if amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return
    tuple_date = extract_data(date)
    if tuple_date is None:
        print(INCORRECT_DATE_MSG)
        return
    if tuple_date not in income_dict:
        income_dict[tuple_date] = 0
    income_dict[tuple_date] += amount
    print(OP_SUCCESS_MSG)


def cost(category_name: str, amount: int, date: str) -> None:
    if amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return
    tuple_date = extract_data(date)
    if tuple_date is None:
        print(INCORRECT_DATE_MSG)
        return
    if tuple_date not in expense_dict:
        expense_dict[tuple_date] = 0
        details_dict[tuple_date] = {}
    expense_dict[tuple_date] += amount
    if category_name not in details_dict[tuple_date]:
        details_dict[tuple_date][category_name] = 0
    details_dict[tuple_date][category_name] += amount
    print(OP_SUCCESS_MSG)


def stats(date: str) -> None:
    tuple_date = extract_data(date)
    if tuple_date is None:
        print(INCORRECT_DATE_MSG)
        return
    categories = count_categories(tuple_date)
    print(f"Your statistics as on {date}:")
    print_capital(tuple_date)
    print_month_profit(tuple_date)
    print("\nDetails (category: amount):")
    if categories:
        for idx, (cat, amount) in enumerate(categories.items(), start=1):
            print(f"{idx}. {cat}: {amount:.0f}")


def print_capital(tuple_date: DataTuple) -> None:
    total_income, total_expense = count_total_income(tuple_date), count_total_expense(tuple_date)
    capital = total_income - total_expense
    print(f"Total capital: {capital:.2f} rubles")


def print_month_profit(tuple_date: DataTuple) -> None:
    month_income, month_expense = count_monthly_income(tuple_date), count_monthly_expense(tuple_date)
    month_profit = month_income - month_expense
    profit_text = "profit was" if month_profit >= 0 else "loss was"
    print(f"This month {profit_text} {abs(month_profit):.2f} rubles")
    print(f"Income: {month_income:.2f} rubles")
    print(f"Expenses: {month_expense:.2f} rubles")


def count_total_income(tuple_date: DataTuple) -> int:
    total_income = 0
    for dt, amount in income_dict.items():
        if compare_date(tuple_date, dt):
            total_income += amount
    return total_income


def count_monthly_income(tuple_date: DataTuple) -> int:
    monthly_income = 0
    for dt, amount in income_dict.items():
        if compare_date(tuple_date, dt) and is_same_month(dt, tuple_date):
            monthly_income += amount
    return monthly_income


def count_total_expense(tuple_date: DataTuple) -> int:
    total_expense = 0
    for dt, amount in expense_dict.items():
        if compare_date(tuple_date, dt):
            total_expense += amount
    return total_expense


def count_monthly_expense(tuple_date: DataTuple) -> int:
    monthly_expense = 0
    for dt, amount in expense_dict.items():
        if compare_date(tuple_date, dt) and is_same_month(dt, tuple_date):
            monthly_expense += amount
    return monthly_expense


def count_categories(tuple_date: DataTuple) -> dict[str, int]:
    categories: dict[str, int] = {}
    for dt, category_dict in details_dict.items():
        if compare_date(tuple_date, dt) and is_same_month(dt, tuple_date):
            for cat, amount in category_dict.items():
                categories[cat] += amount
    return dict(sorted(categories.items()))


def is_same_month(date1: DataTuple, date2: DataTuple) -> bool:
    return date1[1:] == date2[1:]


def compare_date(first: DataTuple, second: DataTuple) -> bool:
    if first[2] != second[2]:
        return first[2] < second[2]
    if first[1] != second[1]:
        return first[1] < second[1]
    return first[0] <= second[0]


def date_validation(day: int, month: int, year: int) -> bool:
    if not (MIN_MONTH <= month <= MAX_MONTH):
        return False
    if day < MIN_DAY:
        return False
    if month in MONTHS_THIRTY_DAYS:
        return day <= MAX_DAY_IN_THIRTY_DAYS_MONTH
    if month == FEBRUARY:
        max_day = MAX_DAY_FEB_LEAP if is_leap_year(year) else MAX_DAY_FEB_NORMAL
        return day <= max_day
    return day <= MAX_DAY_IN_THIRTY_ONE_DAY_MONTH


def main() -> None:
    input_line = input().split()
    if not input_line:
        return
    command = input_line[0]
    match command:
        case "income":
            if len(input_line) == INCOME_ARGS:
                income(int(input_line[1]), input_line[2])
            else:
                print(UNKNOWN_COMMAND_MSG)
        case "cost":
            if len(input_line) == COST_ARGS:
                cost(input_line[1], int(input_line[2]), input_line[3])
            else:
                print(UNKNOWN_COMMAND_MSG)
        case "stats":
            if len(input_line) == STATS_ARGS:
                stats(input_line[1])
            else:
                print(UNKNOWN_COMMAND_MSG)
        case _:
            print(UNKNOWN_COMMAND_MSG)


def is_leap_year(year: int) -> bool:
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0


def extract_data(maybe_dt: str) -> DataTuple | None:
    if len(maybe_dt) == DATE_LENGTH and maybe_dt.count("-"):
        day, month, year = map(int, maybe_dt.split("-"))
        if date_validation(day, month, year):
            return (day, month, year)
    return None


if __name__ == "__main__":
    main()
