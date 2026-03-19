#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"
NUMBER_OF_DATE_PARTS = 3
DATE_SEP = "-"
CategoryStat = tuple[str, float]
CategoryStats = list[CategoryStat]
StatsResult = tuple[float, float, float, CategoryStats]

all_transactions: list[float | list[list[float | str]] | list[list[str | float]]] = [
    0,
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
    leap = year % 4 == 0 and year % 100 != 0
    return leap or year % 400 == 0


def check_date_format(maybe_dt: str) -> bool:

    if maybe_dt is None:
        return False
    if len(maybe_dt.split(DATE_SEP)) != NUMBER_OF_DATE_PARTS:
        return False
    date_sep_in_front_or_back = maybe_dt[0] == DATE_SEP or maybe_dt[-1] == DATE_SEP
    if "--" in maybe_dt or date_sep_in_front_or_back:
        return False

    return all(char in "0123456789-" for char in maybe_dt)


DAYS_IN_MONTH = (
    31,
    28,
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
)


def check_date_bounds(day: int, month: int, year: int) -> bool:
    if month < 1 or month > len(DAYS_IN_MONTH):
        return False

    max_day = DAYS_IN_MONTH[month - 1]
    if month == 2 and is_leap_year(year):
        max_day = 29

    return 1 <= day <= max_day


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    if not check_date_format(maybe_dt):
        return None

    day, month, year = map(int, maybe_dt.split("-"))

    if check_date_bounds(day, month, year):
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


def check_year_bonds(first_year: int, second_year: int) -> bool | None:
    if first_year < second_year:
        return True
    if first_year > second_year:
        return False
    return None


def is_not_later(first_date: str, second_date: str) -> bool:
    first = extract_date(first_date)
    second = extract_date(second_date)

    year_check = check_year_bonds(first[2], second[2])
    if year_check is not None:
        return year_check

    # first_day, first_month, first_year = first
    # second_day, second_month, second_year = second

    if check_year_bonds is not None:
        return check_year_bonds(first[2], second[2])

    if first[1] < second[1]:
        return True
    if first[1] > second[1]:
        return False

    return first[0] <= second[0]


def count_capital(date: str) -> float:
    income_transaction_sum = sum(
        income_transaction[0] for income_transaction in all_transactions[1] if is_not_later(income_transaction[1], date)
    )
    loss_transaction_sum = sum(
        loss_transaction[1] for loss_transaction in all_transactions[2] if is_not_later(loss_transaction[2], date)
    )
    return income_transaction_sum - loss_transaction_sum


def count_loss(target_month: int, target_year: int) -> float:
    return sum(
        loss_in_curr_transaction[1]
        for loss_in_curr_transaction in all_transactions[2]
        if extract_date(loss_in_curr_transaction[2]) is not None
        and extract_date(loss_in_curr_transaction[2])[2] == target_year
        and extract_date(loss_in_curr_transaction[2])[1] == target_month
    )


def count_profit(target_month: int, target_year: int) -> float:
    return sum(
        profit_in_curr_transaction[0]
        for profit_in_curr_transaction in all_transactions[1]
        if extract_date(profit_in_curr_transaction[1]) is not None
        and extract_date(profit_in_curr_transaction[1])[2] == target_year
        and extract_date(profit_in_curr_transaction[1])[1] == target_month
    )


def extract_category_and_amount(target_month: int, target_year: int) -> list[tuple[str, float]]:
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
            dict_of_categories[category] = 0
        dict_of_categories[category] += loss_transaction[1]
    return list(dict_of_categories.items())


def stats_handler(date: str) -> StatsResult:
    parsed_date = extract_date(date)
    if parsed_date is None:
        return 0, 0, 0, []

    _, month, year = parsed_date

    category_stats = extract_category_and_amount(month, year)
    category_stats.sort(key=lambda category: category[0])

    return (
        count_capital(date),
        count_loss(month, year),
        count_profit(month, year),
        category_stats,
    )


def sum_into_float(maybe_float: str) -> float | None:
    for char in maybe_float:
        if char not in "0123456789,.":
            return None
    for char in maybe_float:
        if char in ".," and maybe_float.count(char) > 1:
            return None
    num_of_commas = maybe_float.count(",") + maybe_float.count(".")
    if ("." in maybe_float or num_of_commas == 0) and maybe_float[0] != ".":
        return float(maybe_float)
    num_parts = maybe_float.split(",")
    before_comma = num_parts[0]
    after_comma = num_parts[1]
    return float(f"{before_comma}.{after_comma}")


def format_category_stats(category_stats: CategoryStats) -> str:
    lines = []

    for index, category_stat in enumerate(category_stats, start=1):
        category, amount = category_stat
        lines.append(f"{index}. {category}: {amount}")

    return "\n".join(lines)


def details_handler(date: str) -> str:
    capital, expenses, income, category_stats = stats_handler(date)

    lines = [
        f"Your statistics as of {date}:",
        f"Total capital: {capital} rubles",
        f"Income: {income} rubles",
        f"Expenses: {expenses} rubles",
        "",
        "Breakdown (category: amount):",
    ]

    if category_stats:
        lines.append(format_category_stats(category_stats))

    return "\n".join(lines)


LENGTH_OF_INCOME_COMMAND = 3
LENGTH_OF_COST_COMMAND = 4
LENGTH_OF_STATS_COMMAND = 2
LENGTH_OF_UNKNOWN_COMMAND_LEFT_BOUNDARE = 4
LENGTH_OF_UNKNOWN_COMMAND_RIGHT_BOUNDARE = 1


def income(parts: list[str]) -> str:
    if len(parts) != LENGTH_OF_INCOME_COMMAND or parts[0] != "income":
        return UNKNOWN_COMMAND_MSG

    amount = sum_into_float(parts[1])
    if amount is None:
        return UNKNOWN_COMMAND_MSG

    return income_handler(amount, parts[2])


def cost(parts: list[str]) -> str:
    if len(parts) != LENGTH_OF_COST_COMMAND or parts[0] != "cost":
        return UNKNOWN_COMMAND_MSG

    amount = sum_into_float(parts[2])
    if amount is None:
        return UNKNOWN_COMMAND_MSG

    return cost_handler(parts[1], amount, parts[3])


def stats(parts: list[str]) -> str:
    if len(parts) != LENGTH_OF_STATS_COMMAND or parts[0] != "stats":
        return UNKNOWN_COMMAND_MSG

    if extract_date(parts[1]) is None:
        return INCORRECT_DATE_MSG

    return details_handler(parts[1])


def process_command(parts: list[str]) -> str:
    if not parts:
        return UNKNOWN_COMMAND_MSG

    command_name = parts[0]

    if command_name == "cost":
        return cost(parts)
    if command_name == "income":
        return income(parts)
    if command_name == "stats":
        return stats(parts)

    return UNKNOWN_COMMAND_MSG


def main() -> None:
    command = input()
    while command != "exit":
        command = input()
        parts = command.split()
        print(process_command(parts))


if __name__ == "__main__":
    main()
