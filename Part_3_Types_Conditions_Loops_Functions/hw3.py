#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Неизвестная команда!"
NONPOSITIVE_VALUE_MSG = "Значение должно быть больше нуля!"
INCORRECT_DATE_MSG = "Неправильная дата!"
OP_SUCCESS_MSG = "Добавлено"

DATE_PARTS_COUNT = 3
DAY_DIGITS = 2
MONTH_DIGITS = 2
YEAR_DIGITS = 4
MONTHS_IN_YEAR = 12
INCOME_ARGS = 3
COST_ARGS = 4
STATS_ARGS = 2
FEB_INDEX = 2
FEB_LEAP_DAYS = 29


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    parts = maybe_dt.split("-")

    if len(parts) != DATE_PARTS_COUNT:
        return None

    if len(parts[0]) != DAY_DIGITS or len(parts[1]) != MONTH_DIGITS or len(parts[2]) != YEAR_DIGITS:
        return None

    if not parts[0].isdigit() or not parts[1].isdigit() or not parts[2].isdigit():
        return None

    day, month, year = int(parts[0]), int(parts[1]), int(parts[2])

    if day < 1 or month < 1 or month > MONTHS_IN_YEAR or year < 1:
        return None

    days_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    if is_leap_year(year):
        days_in_month[FEB_INDEX] = FEB_LEAP_DAYS

    if day > days_in_month[month]:
        return None

    return (year, month, day)


def parse_amount(new_amount: float) -> float | None:
    return new_amount if new_amount > 0 else None


def check_category(maybe_cg: str) -> str | None:
    return maybe_cg if len(maybe_cg) > 0 and all(letter.isalpha() for letter in maybe_cg.lower()) else None


def print_stats(amounts: list[tuple[str, float, tuple[int, int, int], str | None]],
                query_date: tuple[int, int, int], pretty_date: str) -> None:
    capital: float = 0
    month_income: float = 0
    month_cost: float = 0
    costs: dict[str, float] = {}

    for rec_type, amount, date, maybe_cg in amounts:
        if date <= query_date:
            capital += amount
            if date[1] == query_date[1] and date[0] == query_date[0]:
                if rec_type == "income":
                    month_income += amount
                else:
                    month_cost += abs(amount)
                    if maybe_cg is not None:
                        costs[maybe_cg] = costs.get(maybe_cg, 0) + abs(amount)

    sorted_costs = sorted(costs.items(), key=lambda x: x[0])
    budget = month_income - month_cost
    budget_label = "убыток составил" if budget < 0 else "прибыль составила"

    print(f"Ваша статистика по состоянию на {pretty_date}:")  # noqa: T201
    print(f"Суммарный капитал: {capital:.2f} рублей")  # noqa: T201
    print(f"В этом месяце {budget_label} {abs(budget):.2f} рублей")  # noqa: T201, RUF001
    print(f"Доходы: {month_income:.2f} рублей")  # noqa: T201
    print(f"Расходы: {month_cost:.2f} рублей")  # noqa: T201
    print()  # noqa: T201
    print("Детализация (категория: сумма):")  # noqa: T201

    for i, (category, value) in enumerate(sorted_costs, 1):
        print(f"{i}. {category}: {int(value) if value == int(value) else value}")  # noqa: T201


def handle_income(parts: list[str], amounts: list[tuple[str, float, tuple[int, int, int], str | None]]) -> None:
    if len(parts) != INCOME_ARGS:
        print(UNKNOWN_COMMAND_MSG)  # noqa: T201
        return

    amount, date = parse_amount(float(parts[1].replace(",", "."))), extract_date(parts[2])

    if amount is None:
        print(NONPOSITIVE_VALUE_MSG)  # noqa: T201
        return

    if date is None:
        print(INCORRECT_DATE_MSG)  # noqa: T201
        return

    amounts.append(("income", amount, date, None))
    print(OP_SUCCESS_MSG)  # noqa: T201


def handle_cost(parts: list[str], amounts: list[tuple[str, float, tuple[int, int, int], str | None]]) -> None:
    if len(parts) != COST_ARGS:
        print(UNKNOWN_COMMAND_MSG)  # noqa: T201
        return

    category = check_category(parts[1])
    amount = parse_amount(float(parts[2].replace(",", ".")))
    date = extract_date(parts[3])

    if category is None:
        print(UNKNOWN_COMMAND_MSG)  # noqa: T201
        return

    if amount is None:
        print(NONPOSITIVE_VALUE_MSG)  # noqa: T201
        return

    if date is None:
        print(INCORRECT_DATE_MSG)  # noqa: T201
        return

    amounts.append(("cost", -amount, date, category))
    print(OP_SUCCESS_MSG)  # noqa: T201


def handle_stats(parts: list[str], amounts: list[tuple[str, float, tuple[int, int, int], str | None]]) -> None:
    if len(parts) != STATS_ARGS:
        print(UNKNOWN_COMMAND_MSG)  # noqa: T201
        return

    pretty_date = parts[1]
    query_date = extract_date(pretty_date)

    if query_date is None:
        print(INCORRECT_DATE_MSG)  # noqa: T201
        return

    print_stats(amounts, query_date, pretty_date)


def main() -> None:
    amounts: list[tuple[str, float, tuple[int, int, int], str | None]] = []

    while True:
        line = input()
        parts = line.split()

        if len(parts) == 0:
            continue

        command = parts[0]

        match command:
            case "income":
                handle_income(parts, amounts)
            case "cost":
                handle_cost(parts, amounts)
            case "stats":
                handle_stats(parts, amounts)
            case _:
                print(UNKNOWN_COMMAND_MSG)  # noqa: T201


if __name__ == "__main__":
    main()
