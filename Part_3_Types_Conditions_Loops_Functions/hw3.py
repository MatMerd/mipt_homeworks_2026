#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"

CAT_KEY = "category_stats"

FEBRUARY = 2
MONTHS_IN_YEAR = 12
DATE_PARTS_COUNT = 3
INCOME_CMD_LEN = 3
COST_CMD_LEN = 4
STATS_CMD_LEN = 2
SHORT_MONTHS = (4, 6, 9, 11)

DateData = tuple[int, int, int]
IncomeData = tuple[int, int, int, float]
ExpenseData = tuple[int, int, int, str, float]
StatsData = dict[str, float]
StatsPair = tuple[StatsData, StatsData]


def get_days_in_month(month: int, year: int) -> int:
    if month == FEBRUARY:
        return 29 if is_leap_year(year) else 28
    if month in SHORT_MONTHS:
        return 30
    return 31


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """

    is_fourth = year % 4 == 0
    is_not_hundredth = year % 100 != 0
    is_four_hundredth = year % 400 == 0
    return (is_fourth and is_not_hundredth) or is_four_hundredth


def extract_date(maybe_dt: str) -> DateData | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """

    parsed = maybe_dt.split("-")
    if len(parsed) != DATE_PARTS_COUNT:
        return None

    for part in parsed:
        if not part.isdigit():
            return None

    year = int(parsed[2])
    month = int(parsed[1])
    if not (year >= 1 and 1 <= month <= MONTHS_IN_YEAR):
        return None

    if 1 <= int(parsed[0]) <= get_days_in_month(month, year):
        return int(parsed[0]), month, year

    return None


def validate_command(command_parts: list[str]) -> bool:
    cmd = command_parts[0]
    cmd_len = len(command_parts)

    if cmd == "income" and cmd_len == INCOME_CMD_LEN:
        return True
    if cmd == "cost" and cmd_len == COST_CMD_LEN:
        return True
    if cmd == "stats" and cmd_len == STATS_CMD_LEN:
        return True

    print(UNKNOWN_COMMAND_MSG)
    return False


def add_expense(cat_stats: StatsData, category: str, amount: float) -> None:
    cat_stats[category] = cat_stats.get(category, 0) + amount


def process_incomes(incomes: list[IncomeData], target_date: DateData, stats: StatsData) -> None:
    for record in incomes:
        if record[:3] <= target_date:
            stats["total_capital"] += record[3]
            if record[:2] == target_date[:2]:
                stats["month_income"] += record[3]


def process_expenses(
    expenses: list[ExpenseData],
    target_date: DateData,
    stats: StatsData,
    cat_stats: StatsData,
) -> None:
    for record in expenses:
        if record[:3] <= target_date:
            stats["total_capital"] -= record[4]
            if record[:2] == target_date[:2]:
                stats["month_expense"] += record[4]
                add_expense(cat_stats, record[3], record[4])


def collect_statistic(
    incomes: list[IncomeData],
    expenses: list[ExpenseData],
    target_date: DateData,
) -> StatsPair:
    stats: StatsData = {}
    stats["total_capital"] = 0
    stats["month_income"] = 0
    stats["month_expense"] = 0
    cat_stats: StatsData = {}
    process_incomes(incomes, target_date, stats)
    process_expenses(expenses, target_date, stats, cat_stats)
    return stats, cat_stats


def print_categories(cat_dict: StatsData) -> None:
    for index, cat_data in enumerate(sorted(cat_dict.items()), start=1):
        amount = cat_data[1]
        if amount == int(amount):
            print(f"{index}. {cat_data[0]}: {int(amount)}")
        else:
            print(f"{index}. {cat_data[0]}: {amount}")


def print_stat(stats_data: StatsPair, date_str: str) -> None:
    stats = stats_data[0]
    result_val = stats["month_income"] - stats["month_expense"]
    result_type = "the profit amounted" if result_val >= 0 else "the loss amounted to"

    print(f"Your statistics as of {date_str}:")
    print(f"Total capital: {stats['total_capital']:.2f} rubles")
    print(f"This month, {result_type} to {abs(result_val):.2f} rubles.")
    print(f"Income: {stats['month_income']:.2f} rubles")
    print(f"Expenses: {stats['month_expense']:.2f} rubles")
    print("\nDetails (category: amount):")

    print_categories(stats_data[1])


def make_income(raw_date: DateData, amount: float) -> IncomeData:
    return raw_date[2], raw_date[1], raw_date[0], amount


def make_expense(
    raw_date: DateData,
    category: str,
    amount: float,
) -> ExpenseData:
    return raw_date[2], raw_date[1], raw_date[0], category, amount


def income_handler(command: list[str], incomes: list[IncomeData]) -> None:
    amount = float(command[1])
    if amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return
    raw_date = extract_date(command[-1])
    if raw_date is None:
        print(INCORRECT_DATE_MSG)
        return
    incomes.append(make_income(raw_date, amount))
    print(OP_SUCCESS_MSG)


def cost_handler(command: list[str], expenses: list[ExpenseData]) -> None:
    amount = float(command[2])
    if amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return
    raw_date = extract_date(command[-1])
    if raw_date is None:
        print(INCORRECT_DATE_MSG)
        return
    expenses.append(make_expense(raw_date, command[1], amount))
    print(OP_SUCCESS_MSG)


def stats_handler(
    command: list[str],
    incomes: list[IncomeData],
    expenses: list[ExpenseData],
) -> None:
    raw_date = extract_date(command[-1])
    if raw_date is None:
        print(INCORRECT_DATE_MSG)
        return

    target_date = (raw_date[2], raw_date[1], raw_date[0])
    print_stat(collect_statistic(incomes, expenses, target_date), command[-1])


def process_command(
    command_str: str,
    incomes: list[IncomeData],
    expenses: list[ExpenseData],
) -> None:
    command = command_str.replace(",", ".").split()
    if not command or not validate_command(command):
        return

    cmd = command[0]
    if cmd == "income":
        income_handler(command, incomes)
    elif cmd == "cost":
        cost_handler(command, expenses)
    elif cmd == "stats":
        stats_handler(command, incomes, expenses)


def main() -> None:
    incomes_list: list[IncomeData] = []
    expenses_list: list[ExpenseData] = []
    is_running = True

    while is_running:
        command_str = input()
        process_command(command_str, incomes_list, expenses_list)


if __name__ == "__main__":
    main()
