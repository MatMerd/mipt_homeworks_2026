#!/usr/bin/env python
# ruff: noqa: RUF001

UNKNOWN_COMMAND_MSG = "Неизвестная команда!"
NONPOSITIVE_VALUE_MSG = "Значение должно быть больше нуля!"
INCORRECT_DATE_MSG = "Неправильная дата!"
OP_SUCCESS_MSG = "Добавлено"

CMD_INCOME = "income"
CMD_COST = "cost"
CMD_STATS = "stats"

DATE_LEN = 10
MONTHS_IN_YEAR = 12
FEBRUARY = 2
INCOME_ARGS = 3
COST_ARGS = 4
STATS_ARGS = 2

Income = tuple[int, int, int, float]
Cost = tuple[int, int, int, str, float]

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
    if len(maybe_dt) != DATE_LEN:
        return None
    if maybe_dt[2] != "-" or maybe_dt[5] != "-":
        return None

    day_str = maybe_dt[:2]
    month_str = maybe_dt[3:5]
    year_str = maybe_dt[6:10]

    if not (day_str.isdigit() and month_str.isdigit() and year_str.isdigit()):
        return None

    day = int(day_str)
    month = int(month_str)
    year = int(year_str)

    if month < 1 or month > MONTHS_IN_YEAR:
        return None

    days_in_month = 31
    if month in (4, 6, 9, 11):
        days_in_month = 30
    elif month == FEBRUARY:
        days_in_month = 29 if is_leap_year(year) else 28

    if day < 1 or day > days_in_month:
        return None

    return day, month, year


def parse_price(maybe_amount: str) -> float | None:
    """
    Парсит цену из строки.

    :param str maybe_amount: Проверяемая строка
    :return: Числовое значение цены или None, если цена неправильная.
    :rtype: float | None
    """
    normalized = maybe_amount.replace(",", ".")
    if normalized.startswith("-"):
        return None
    if not normalized:
        return None
    normalized = normalized.removeprefix("+")
    if not normalized or normalized.count(".") > 1:
        return None

    if "." in normalized:
        left, right = normalized.split(".", 1)
        is_valid = bool(left) and bool(right) and left.isdigit() and right.isdigit()
    else:
        is_valid = normalized.isdigit()

    if not is_valid:
        return None

    value = float(normalized)
    if value <= 0:
        return None
    return value


def check_date(a: tuple[int, int, int], b: tuple[int, int, int]) -> bool:
    """
    Проверяет, что дата a не позже даты b.

    :param tuple[int, int, int] a: Дата a в формате (день, месяц, год)
    :param tuple[int, int, int] b: Дата b в формате (день, месяц, год)
    :return: True, если a не позже b, иначе False.
    :rtype: bool
    """
    day_a, month_a, year_a = a
    day_b, month_b, year_b = b
    return (year_a, month_a, day_a) <= (year_b, month_b, day_b)


def money_formater(value: float) -> str:
    """
    Форматирует сумму денег в строку.

    :param float value: Сумма денег
    :return: Отформатированная строка.
    :rtype: str
    """
    if value.is_integer():
        return str(int(value))
    formatted = f"{value:.2f}"
    return formatted.rstrip("0").rstrip(".")


def collect_stats(
    incomes: list[Income],
    costs: list[Cost],
    cur_date: tuple[int, int, int],
) -> tuple[float, float, float, float, dict[str, float]]:
    """Собирает статистику на указанную дату."""
    _, query_month, query_year = cur_date

    total_plus = 0.0
    total_price = 0.0
    month_plus = 0.0
    month_price = 0.0
    categories: dict[str, float] = {}

    for inc_day, inc_month, inc_year, amount in incomes:
        inc_date = (inc_day, inc_month, inc_year)
        if check_date(inc_date, cur_date):
            total_plus += amount
            if inc_month == query_month and inc_year == query_year:
                month_plus += amount

    for day, month, year, category, amount in costs:
        cost_date = (day, month, year)
        if not check_date(cost_date, cur_date):
            continue
        total_price += amount
        if month != query_month or year != query_year:
            continue
        month_price += amount
        categories[category] = categories.get(category, 0.0) + amount

    return total_plus, total_price, month_plus, month_price, categories


def build_stats_output(
    parts: list[str],
    cur_date: tuple[int, int, int],
    incomes: list[Income],
    costs: list[Cost],
) -> list[str]:
    """
    Формирует строки вывода для команды stats.

    :param list[str] parts: Части команды stats
    :param tuple[int, int, int] cur_date: Дата для статистики
    :param list[Income] incomes: Список доходов
    :param list[Cost] costs: Список расходов
    :return: Список строк для вывода.
    :rtype: list[str]
    """
    total_plus, total_price, month_plus, month_price, categories = collect_stats(incomes, costs, cur_date)

    month_diff = month_plus - month_price
    total_capital = total_plus - total_price
    lines = [
        f"Ваша статистика по состоянию на {parts[1]}:",
        f"Суммарный капитал: {total_capital:.2f} рублей",
    ]
    if month_diff >= 0:
        lines.append(f"В этом месяце прибыль составила {month_diff:.2f} рублей")
    else:
        lines.append(f"В этом месяце убыток составил {abs(month_diff):.2f} рублей")

    lines.extend(
        [
            f"Доходы: {month_plus:.2f} рублей",
            f"Расходы: {month_price:.2f} рублей",
            "",
            "Детализация (категория: сумма):",
        ],
    )
    for index, category_name in enumerate(sorted(categories), start=1):
        value = money_formater(categories[category_name])
        lines.append(f"{index}. {category_name}: {value}")

    return lines


def handle_income(parts: list[str], incomes: list[Income]) -> None:
    """Обрабатывает команду income."""
    if len(parts) != INCOME_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount = parse_price(parts[1])
    if amount is None:
        print(NONPOSITIVE_VALUE_MSG)
        return

    date_tuple = extract_date(parts[2])
    if date_tuple is None:
        print(INCORRECT_DATE_MSG)
        return

    day, month, year = date_tuple
    incomes.append((day, month, year, amount))
    print(OP_SUCCESS_MSG)


def handle_cost(parts: list[str], costs: list[Cost]) -> None:
    """Обрабатывает команду cost."""
    if len(parts) != COST_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return

    category = parts[1]
    if not category or "." in category or "," in category:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount = parse_price(parts[2])
    if amount is None:
        print(NONPOSITIVE_VALUE_MSG)
        return

    date_tuple = extract_date(parts[3])
    if date_tuple is None:
        print(INCORRECT_DATE_MSG)
        return

    day, month, year = date_tuple
    costs.append((day, month, year, category, amount))
    print(OP_SUCCESS_MSG)


def handle_stats(parts: list[str], incomes: list[Income], costs: list[Cost]) -> None:
    """Обрабатывает команду stats."""
    if len(parts) != STATS_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return

    cur_date = extract_date(parts[1])
    if cur_date is None:
        print(INCORRECT_DATE_MSG)
        return

    print("\n".join(build_stats_output(parts, cur_date, incomes, costs)))


def main() -> None:
    incomes: list[Income] = []
    costs: list[Cost] = []

    while True:
        line = input().strip()

        if not line:
            continue

        parts = line.split()
        command = parts[0]

        if command == CMD_INCOME:
            handle_income(parts, incomes)
            continue
        if command == CMD_COST:
            handle_cost(parts, costs)
            continue
        if command == CMD_STATS:
            handle_stats(parts, incomes, costs)
            continue
        print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()

