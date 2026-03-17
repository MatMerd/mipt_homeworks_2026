#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: tuple формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    date_parts = maybe_dt.split("-")

    if len(date_parts) != 3:
        return None

    for idx, val in enumerate(date_parts):
        if not val.isdigit():
            return None
        date_parts[idx] = int(val)
    day, month, year = date_parts

    if month < 1 or month > 12:
        return None
    if day < 1:
        return None
    if month in (1, 3, 5, 7, 8, 10, 12) and day > 31:
        return None
    if month in (4, 6, 9, 11) and day > 30:
        return None
    if month == 2:
        if is_leap_year(year) and day > 29:
            return None
        if not is_leap_year(year) and day > 28:
            return None

    return day, month, year


def income_handler(amount: float, income_date: str) -> str:
    return f"{OP_SUCCESS_MSG} {amount=} {income_date=}"


def cost_handler(category_name: str, amount: float, cost_date: str) -> str:
    return f"{OP_SUCCESS_MSG} {category_name=} {amount=} {cost_date=}"


def handle_income(incomes: list[tuple[float, str]], amount_str: str, income_date: str) -> str:
    amount: float | None = parse_amount(amount_str)
    if amount is None:
        return UNKNOWN_COMMAND_MSG
    if not amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    date: tuple[int, int, int] | None = extract_date(income_date)
    if date is None:
        return INCORRECT_DATE_MSG

    incomes.append((amount, income_date))
    return income_handler(amount, income_date)


def handle_cost(costs: list[tuple[str, float, tuple[int, int, int]]], category_name: str, amount_str: str,
                cost_date: str) -> str:
    if category_name.strip() == "":
        return UNKNOWN_COMMAND_MSG

    amount: float | None = parse_amount(amount_str)
    if amount is None:
        return UNKNOWN_COMMAND_MSG
    if not amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    date: tuple[int, int, int] | None = extract_date(cost_date)
    if date is None:
        return INCORRECT_DATE_MSG

    costs.append((category_name, amount, date))
    return cost_handler(category_name, amount, cost_date)


def date_key(date_tuple: tuple[int, int, int]) -> tuple[int, int, int]:
    """Преобразует дату в кортеж формата (год, месяц, день) для удобства сравнения."""
    day, month, year = date_tuple
    return year, month, day


def is_not_later(record_date: tuple[int, int, int], border_date: tuple[int, int, int]) -> bool:
    return date_key(record_date) <= date_key(border_date)


def is_same_month(record_date: tuple[int, int, int], border_date: tuple[int, int, int]) -> bool:
    _, record_month, record_year = record_date
    _, border_month, border_year = border_date
    return record_month == border_month and record_year == border_year


def format_category_amount(amount: float) -> str:
    if amount.is_integer():
        return str(int(amount))

    return f"{amount:.10f}".rstrip("0").rstrip(".")


def show_stats(incomes: list[tuple[float, str]], costs: list[tuple[str, float, tuple[int, int, int]]],
               date: str) -> str:
    stats_date = extract_date(date)
    if stats_date is None:
        return INCORRECT_DATE_MSG

    total_capital = 0.0
    month_income = 0.0
    month_cost = 0.0
    categories: dict[str, float] = {}

    for amount, income_date_str in incomes:
        income_date = extract_date(income_date_str)
        if income_date is None or not is_not_later(income_date, stats_date):
            continue

        total_capital += amount
        if is_same_month(income_date, stats_date):
            month_income += amount

    for category_name, amount, cost_date in costs:
        if not is_not_later(cost_date, stats_date):
            continue

        total_capital -= amount
        if not is_same_month(cost_date, stats_date):
            continue

        month_cost += amount
        if category_name not in categories:
            categories[category_name] = 0.0
        categories[category_name] += amount

    profit = month_income - month_cost
    result = "прибыль составила"
    if profit < 0:
        result = "убыток составил"
        profit = -profit

    lines = [
        f"Ваша статистика по состоянию на {date}:",
        f"Суммарный капитал: {total_capital:.2f} рублей",
        f"В этом месяце {result} {profit:.2f} рублей",
        f"Доходы: {month_income:.2f} рублей",
        f"Расходы: {month_cost:.2f} рублей",
        "",
        "Детализация (категория: сумма):",
    ]

    for idx, category_name in enumerate(sorted(categories), start=1):
        category_total = format_category_amount(categories[category_name])
        lines.append(f"{idx}. {category_name}: {category_total}")

    return "\n".join(lines)


def parse_amount(raw: str) -> float | None:
    if raw.strip() == "":
        return None

    sign = ""
    if raw[0] in "+-":
        sign = raw[0]
        raw = raw[1:]

    if raw.strip() == "":
        return None

    normalized = raw.replace(",", ".")
    if normalized.count(".") > 1:
        return None

    if "." in normalized:
        left, right = normalized.split(".", 1)
        if left.strip() == "" or right.strip() == "":
            return None
        if not left.isdigit() or not right.isdigit():
            return None
    else:
        if not normalized.isdigit():
            return None

    return float(sign + normalized)


def main() -> None:
    incomes: list[tuple[float, str]] = []
    costs: list[tuple[str, float, tuple[int, int, int]]] = []

    while True:
        raw = input().strip()
        if raw == "":
            break

        parts = raw.split()

        if len(parts) == 3 and parts[0] == "income":
            print(handle_income(incomes, parts[1], parts[2]))
        elif len(parts) == 4 and parts[0] == "cost":
            print(handle_cost(costs, parts[1], parts[2], parts[3]))
        elif len(parts) == 2 and parts[0] == "stats":
            print(show_stats(incomes, costs, parts[1]))
        else:
            print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()
