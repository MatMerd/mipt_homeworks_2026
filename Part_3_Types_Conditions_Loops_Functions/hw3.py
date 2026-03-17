#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Неизвестная команда!"
NONPOSITIVE_VALUE_MSG = "Значение должно быть больше нуля!"
INCORRECT_DATE_MSG = "Неправильная дата!"
OP_SUCCESS_MSG = "Добавлено"

DATE_SIZE = 3
INCOME_SIZE = 2
EXPENSE_SIZE = 3
NUMBER_OF_MONTHS = 12

DAY_LEN = 2
MONTH_LEN = 2

FEBRUARY = 2
DAYS_IN_LEAP_FEBRUARY = 29
NUMBERS_OF_DAYS = {
    1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 30,
    9: 31,
    10: 31,
    11: 30,
    12: 31
}

IncomeHistory = list[tuple[float, int, int, int]]
ExpenseHistory = list[tuple[str, float, int, int, int]]


def is_leap_year(year: int) -> bool:
    return bool((year % 4 == 0 and year % 100 != 0) or year % 400 == 0)


def earlier(date1: tuple, date2: tuple[int, int, int]) -> bool:
    return bool(date1[2] < date2[2] or
                (date1[2] == date2[2] and date1[1] < date2[1]) or
                (date1[2] == date2[2] and date1[1] == date2[1] and date1[0] <= date2[0]))


def date_is_valid(date: list[str]) -> bool:
    return bool(len(date[0]) == DAY_LEN and len(date[1]) == MONTH_LEN)


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    split_dt = maybe_dt.split("-")
    if len(split_dt) != DATE_SIZE or not(date_is_valid(split_dt)) or not(1 <= int(split_dt[1]) <= NUMBER_OF_MONTHS):
        return None

    if int(split_dt[1]) == FEBRUARY and is_leap_year(int(split_dt[2])):
        if int(split_dt[0]) > DAYS_IN_LEAP_FEBRUARY or int(split_dt[0]) < 1:
            return None
        return int(split_dt[0]), int(split_dt[1]), int(split_dt[2])

    if int(split_dt[0]) > NUMBERS_OF_DAYS[int(split_dt[1])] or int(split_dt[0]) < 1:
        return None
    return int(split_dt[0]), int(split_dt[1]), int(split_dt[2])


def extract_sum(maybe_sum: str) -> float | None:
    if maybe_sum == "":
        return None

    maybe_sum = maybe_sum.replace(",", ".")

    if maybe_sum[0] == "." or maybe_sum.count(".") > 1:
        return None

    if maybe_sum[0] == "-":
        for char in maybe_sum[1:]:
            if not(char.isdigit() or char == "."):
                return None
        return float(maybe_sum)

    for char in maybe_sum:
        if not(char.isdigit() or char == "."):
            return None
    return float(maybe_sum)


def extract_category(maybe_category: str) -> bool:
    category = maybe_category.split()
    return not (len(category) != 1 or category[0].count(".") > 0 or category[0].count(",") > 0)


def iter_input_lines() -> list[str]:
    with open(0) as stdin:
        return stdin.readlines()


def income_processing(command: list[str], incomes: IncomeHistory) -> None:
    if len(command) != INCOME_SIZE:
        print(UNKNOWN_COMMAND_MSG)
        return

    value = extract_sum(command[0])
    date = extract_date(command[1])

    if value is None:
        print(UNKNOWN_COMMAND_MSG)
        return

    if value <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return

    if date is None:
        print(INCORRECT_DATE_MSG)
        return

    day, month, year = date
    incomes.append((value, day, month, year))

    print(OP_SUCCESS_MSG)
    return


def expense_processing(command: list[str], expenses: ExpenseHistory) -> None:
    if len(command) != EXPENSE_SIZE or not(extract_category(command[0])):
        print(UNKNOWN_COMMAND_MSG)
        return

    value = extract_sum(command[1])
    date = extract_date(command[2])

    if value is None:
        print(UNKNOWN_COMMAND_MSG)
        return

    if value <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return

    if date is None:
        print(INCORRECT_DATE_MSG)
        return

    day, month, year = date
    expenses.append((command[0], value, day, month, year))

    print(OP_SUCCESS_MSG)
    return


def stats_processing(command: list[str], incomes: IncomeHistory, expenses: ExpenseHistory) -> None:
    if len(command) != 1:
        print(UNKNOWN_COMMAND_MSG)
        return

    date = extract_date(command[0])

    if date is None:
        print(INCORRECT_DATE_MSG)
        return

    list_income = [x for x in incomes if earlier(x[1:], date)]
    list_expense = [x for x in expenses if earlier(x[2:], date)]

    print(f"Ваша статистика по состоянию на {command[0]}:")
    print(f"Суммарный капитал: {"{:.2f}".format(sum(x[0] for x in list_income) -
                                                sum(x[1] for x in list_expense))} рублей")

    month_income = sum(x[0] for x in list_income if (x[2] == date[1]) and (x[3] == date[2]))
    list_month_expense = [x for x in list_expense if (x[3] == date[1]) and (x[4] == date[2])]
    month_expense = sum(x[1] for x in list_month_expense)

    if month_income >= month_expense:
        print(f"В этом месяце прибыль составила {f"{month_income - month_expense:.2f}"} рублей")  # noqa: RUF001
    else:
        print(f"В этом месяце убыток составил {f"{month_expense - month_income:.2f}"} рублей")  # noqa: RUF001

    print(f"Доходы: {f"{month_income:.2f}"} рублей")
    print(f"Расходы: {f"{month_expense:.2f}"} рублей")
    print()
    print("Детализация (категория: сумма):")

    if len(list_month_expense) > 0:
        list_month_expense.sort()
        current_category = list_month_expense[0][1]
        category_number = 1
        for x in range(1, len(list_month_expense)):
            if list_month_expense[x][0] == list_month_expense[x - 1][0]:
                current_category += list_month_expense[x][1]
            else:
                print(f"{category_number}. {list_month_expense[x - 1][0]}: {round(current_category)}")
                current_category = list_month_expense[x][1]
                category_number += 1
        print(f"{category_number}. {list_month_expense[len(list_month_expense) - 1][0]}: {round(current_category)}")

    return



def process_line(line: str, incomes: IncomeHistory, expenses: ExpenseHistory) -> None:
    command = line.split()
    if not command:
        print(UNKNOWN_COMMAND_MSG)
        return

    command_name = command[0]
    if command_name == "income":
        income_processing(command[1:], incomes)
        return

    if command_name == "cost":
        expense_processing(command[1:], expenses)
        return

    if command_name == "stats":
        stats_processing(command[1:], incomes, expenses)
        return

    print(UNKNOWN_COMMAND_MSG)

def main() -> None:
    incomes : IncomeHistory = []
    expenses : ExpenseHistory = []

    while True:
        line = input()
        if not line:
            break
        process_line(line, incomes, expenses)


if __name__ == "__main__":
    main()
