#!/usr/bin/env python

income_dict: dict[tuple[int, int, int], float] = {}
expense_dict: dict[tuple[int, int, int], float] = {}
details_dict: dict[tuple[int, int, int], dict[str, float]] = {}

MONTHS_30_DAYS = [4, 6, 9, 11]
FEBRUARY = 2
MIN_MONTH = 1
MAX_MONTH = 12
MIN_DAY = 1
MAX_DAY_30 = 30
MAX_DAY_31 = 31
MAX_DAY_FEB_LEAP = 29
MAX_DAY_FEB_NORMAL = 28
DATE_LENGTH = 10
INCOME_ARGS = 3
COST_ARGS = 4
STATS_ARGS = 2

UNKNOWN_COMMAND_MSG = "Неизвестная команда!"
NONPOSITIVE_VALUE_MSG = "Значение должно быть больше нуля!"
INCORRECT_DATE_MSG = "Неправильная дата!"
OP_SUCCESS_MSG = "Добавлено"

def income(amount: float, date: str) -> None:
    if amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return
    tuple_date = extract_data(date)
    if tuple_date is None:
        print(INCORRECT_DATE_MSG)
        return
    if tuple_date not in income_dict:
        income_dict[tuple_date] = 0.0
    income_dict[tuple_date] += amount
    print(OP_SUCCESS_MSG)

def cost(category_name: str, amount: float, date: str) -> None:
    if amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return
    tuple_date = extract_data(date)
    if tuple_date is None:
        print(INCORRECT_DATE_MSG)
        return
    if tuple_date not in expense_dict:
        expense_dict[tuple_date] = 0.0
        details_dict[tuple_date] = {}
    expense_dict[tuple_date] += amount
    if category_name not in details_dict[tuple_date]:
        details_dict[tuple_date][category_name] = 0.0
    details_dict[tuple_date][category_name] += amount
    print(OP_SUCCESS_MSG)


def stats(date: str) -> None:
    tuple_date = extract_data(date)
    if tuple_date is None:
        print(INCORRECT_DATE_MSG)
        return
    total_income = 0.0
    total_expense = 0.0
    monthly_income = 0.0
    monthly_expense = 0.0
    categories = {}
    for dt, amount in income_dict.items():
        if compare_date(tuple_date, dt) and tuple_date[1:] == dt[1:]:
            total_income += amount
            monthly_income += amount
    for dt, amount in expense_dict.items():
        if compare_date(tuple_date, dt) and tuple_date[1:] == dt[1:]:
            total_expense += amount
            monthly_expense += amount
            categories.update(details_dict[dt])
    capital = total_income - total_expense
    profit = monthly_income - monthly_expense
    profit_text = "прибыль составила" if profit >= 0 else "убыток составил"
    print(f"Ваша статистика по состоянию на {date}:")
    print(f"Суммарный капитал: {capital:.2f} рублей")
    print(f"В этом месяце {profit_text} {abs(profit):.2f} рублей")
    print(f"Доходы: {monthly_income:.2f} рублей")
    print(f"Расходы: {monthly_expense:.2f} рублей")
    print("\nДетализация (категория: сумма):")
    if categories:
        sorted_categories = dict(sorted(categories.items()))
        for idx, (cat, amount) in enumerate(sorted_categories.items(), start=1):
            print(f"{idx}. {cat}: {amount:.0f}")

def compare_date(first: tuple[int, int, int], second: tuple[int, int, int]) -> bool:
    """Возвращает True, если первая дата >= второй"""
    fday, fmonth, fyear = first
    sday, smonth, syear = second
    if fyear < syear:
        return False
    if fyear > syear:
        return True
    if fmonth < smonth:
        return False
    if fmonth > smonth:
        return True
    return fday >= sday


def date_validation(day: int, month: int, year: int) -> bool:
    if not (MIN_MONTH <= month <= MAX_MONTH):
        return False
    if day < MIN_DAY:
        return False
    if month in MONTHS_30_DAYS:
        return day <= MAX_DAY_30
    if month == FEBRUARY:
        max_day = MAX_DAY_FEB_LEAP if is_leap_year(year) else MAX_DAY_FEB_NORMAL
        return day <= max_day
    return day <= MAX_DAY_31


def main() -> None:
    input_line = input().split()
    if not input_line:
        return
    command = input_line[0]
    match command:
        case "income":
            if len(input_line) == INCOME_ARGS:
                income(float(input_line[1]), input_line[2])
            else:
                print(UNKNOWN_COMMAND_MSG)
        case "cost":
            if len(input_line) == COST_ARGS:
                cost(input_line[1], float(input_line[2]), input_line[3])
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
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def extract_data(maybe_dt: str) -> tuple[int, int, int] | None:
    if len(maybe_dt) != DATE_LENGTH:
        return None
    parts = maybe_dt.split("-")
    if len(parts) != 3:
        return None
    try:
        day, month, year = map(int, parts)
    except ValueError:
        return None
    if date_validation(day, month, year):
        return (day, month, year)
    return None

if __name__ == "__main__":
    main()
