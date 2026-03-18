#!/usr/bin/env python

from calendar import month


UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"
NUMBER_OF_DATE_PARTS = 3

all_transactions: list[float | list[list[float | str]] | list[list[str | float]]] = [
    0.0,
    [],
    [],
]


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """

    if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
        return True
    return False


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    if maybe_dt is None:
        return None
    if len(maybe_dt.split("-")) != NUMBER_OF_DATE_PARTS:
        return None
    if (
        "--" in maybe_dt
        or maybe_dt[0] == "-"
        or maybe_dt[-1] == "-"
        or "---" in maybe_dt
    ):
        return None
    for char in maybe_dt:
        if char not in "0123456789-":
            return None
    maybe_dt = maybe_dt.split("-")
    day = int(maybe_dt[0])
    month = int(maybe_dt[1])
    year = int(maybe_dt[2])

    MONTH_NUMBER_BOUNDS = [1, 12]
    NUMBER_OF_DAYS_IN_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if is_leap_year(year):
        NUMBER_OF_DAYS_IN_MONTH[1] = 29
    else:
        NUMBER_OF_DAYS_IN_MONTH[1] = 28
    if month < 1 or month > 12:
        return None

    max_day = NUMBER_OF_DAYS_IN_MONTH[month - 1]
    if day < 1 or day > max_day:
        return None

    return day, month, year


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG
    if extract_date(income_date) is None:
        return INCORRECT_DATE_MSG

    all_transactions[1].append([amount, income_date])
    all_transactions[0] += amount
    return OP_SUCCESS_MSG


def cost_handler(category: str, amount: float, cost_date: str) -> str:
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG
    if extract_date(cost_date) is None:
        return INCORRECT_DATE_MSG

    all_transactions[2].append([category, amount, cost_date])
    all_transactions[0] -= amount
    return OP_SUCCESS_MSG


def is_not_later(first_date: str, second_date: str) -> bool:
    first = extract_date(first_date)
    second = extract_date(second_date)

    if first is None or second is None:
        return False

    first_day, first_month, first_year = first
    second_day, second_month, second_year = second

    if first_year < second_year:
        return True
    if first_year > second_year:
        return False

    if first_month < second_month:
        return True
    if first_month > second_month:
        return False

    return first_day <= second_day


def stats_handler(date: str) -> tuple[float, float, float, list[tuple[str, float]]]:
    parsed_date = extract_date(date)
    if parsed_date is None:
        return 0.0, 0.0, 0.0, []

    _, target_month, target_year = parsed_date

    capital = sum(
        income_transaction[0]
        for income_transaction in all_transactions[1]
        if is_not_later(income_transaction[1], date)
    ) - sum(
        loss_transaction[1]
        for loss_transaction in all_transactions[2]
        if is_not_later(loss_transaction[2], date)
    )

    loss = sum(
        loss_in_curr_transaction[1]
        for loss_in_curr_transaction in all_transactions[2]
        if extract_date(loss_in_curr_transaction[2]) is not None
        and extract_date(loss_in_curr_transaction[2])[2] == target_year
        and extract_date(loss_in_curr_transaction[2])[1] == target_month
    )

    profit = sum(
        profit_in_curr_transaction[0]
        for profit_in_curr_transaction in all_transactions[1]
        if extract_date(profit_in_curr_transaction[1]) is not None
        and extract_date(profit_in_curr_transaction[1])[2] == target_year
        and extract_date(profit_in_curr_transaction[1])[1] == target_month
    )

    loss_list = [
        loss_in_curr_transaction
        for loss_in_curr_transaction in all_transactions[2]
        if extract_date(loss_in_curr_transaction[2]) is not None
        and extract_date(loss_in_curr_transaction[2])[2] == target_year
        and extract_date(loss_in_curr_transaction[2])[1] == target_month
    ]

    dict_of_categories: dict[str, float] = {}
    for loss_transaction in loss_list:
        category = loss_transaction[0]
        if category not in dict_of_categories:
            dict_of_categories[category] = 0.0
        dict_of_categories[category] += loss_transaction[1]

    list_of_categories = list(dict_of_categories.items())
    list_of_categories.sort(key=lambda loss_transaction: loss_transaction[0])

    return capital, loss, profit, list_of_categories


def sum_into_float(maybe_float: str) -> float | None:
    for char in maybe_float:
        if char not in "0123456789,.":
            return None
    for char in maybe_float:
        if char in ".," and maybe_float.count(char) > 1:
            return None
    if (
        "." in maybe_float or maybe_float.count(",") + maybe_float.count(".") == 0
    ) and maybe_float[0] != ".":
        return float(maybe_float)
    return float(f"{maybe_float.split(',')[0]}.{maybe_float.split(',')[1]}")


def details_handler(date: str) -> str:
    stats_info = stats_handler(date)
    details = "\n".join(
        f"{i}. {category}: {amount}"
        for i, (category, amount) in enumerate(stats_info[3], start=1)
    )
    if details == "":
        if stats_info[2] - stats_info[1] >= 0:
            return (
                f"Your statistics as of {date}:\n"
                f"Total capital: {stats_info[0]} rubles\n"
                f"This month's profit: {stats_info[2] - stats_info[1]} rubles\n"
                f"Income: {stats_info[2]} rubles\n"
                f"Expenses: {stats_info[1]} rubles\n\n"
                f"Breakdown (category: amount):"
            )
        else:
            return (
                f"Your statistics as of {date}:\n"
                f"Total capital: {stats_info[0]} rubles\n"
                f"This month's loss: {stats_info[1] - stats_info[2]} rubles\n"
                f"Income: {stats_info[2]} rubles\n"
                f"Expenses: {stats_info[1]} rubles\n\n"
                f"Breakdown (category: amount):"
            )
    elif stats_info[2] - stats_info[1] >= 0:
        return (
            f"Your statistics as of {date}:\n"
            f"Total capital: {stats_info[0]} rubles\n"
            f"This month's profit: {stats_info[2] - stats_info[1]} rubles\n"
            f"Income: {stats_info[2]} rubles\n"
            f"Expenses: {stats_info[1]} rubles\n\n"
            f"Breakdown (category: amount):\n{details}"
        )

    return (
        f"Your statistics as of {date}:\n"
        f"Total capital: {stats_info[0]} rubles\n"
        f"This month's loss: {stats_info[1] - stats_info[2]} rubles\n"
        f"Income: {stats_info[2]} rubles\n"
        f"Expenses: {stats_info[1]} rubles\n\n"
        f"Breakdown (category: amount):\n{details}"
    )


LENGTH_OF_INCOME_COMMAND = 3
LENGTH_OF_COST_COMMAND = 4
LENGTH_OF_STATS_COMMAND = 2
LENGTH_OF_UNKNOWN_COMMAND_LEFT_BOUNDARE = 4
LENGTH_OF_UNKNOWN_COMMAND_RIGHT_BOUNDARE = 1


def main() -> None:
    while True:
        command = input()
        parts = command.split()

        if (
            len(parts) < LENGTH_OF_UNKNOWN_COMMAND_RIGHT_BOUNDARE
            or len(parts) > LENGTH_OF_UNKNOWN_COMMAND_LEFT_BOUNDARE
        ):
            print(UNKNOWN_COMMAND_MSG)

        elif len(parts) == LENGTH_OF_INCOME_COMMAND and parts[0] == "income":
            amount = sum_into_float(parts[1])
            if amount is None:
                print(UNKNOWN_COMMAND_MSG)
            else:
                res = income_handler(amount, parts[2])
                print(res)

        elif len(parts) == LENGTH_OF_COST_COMMAND and parts[0] == "cost":
            amount = sum_into_float(parts[2])
            if amount is None:
                print(UNKNOWN_COMMAND_MSG)
            else:
                res = cost_handler(parts[1], amount, parts[3])
                print(res)

        elif len(parts) == LENGTH_OF_STATS_COMMAND and parts[0] == "stats":
            if extract_date(parts[1]) is None:
                print(INCORRECT_DATE_MSG)
            else:
                stats_info = details_handler(parts[1])
                print(stats_info)

        else:
            print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()
