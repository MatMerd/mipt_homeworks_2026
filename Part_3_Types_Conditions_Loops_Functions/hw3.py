#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Неизвестная команда!"
NONPOSITIVE_VALUE_MSG = "Значение должно быть больше нуля!"
INCORRECT_DATE_MSG = "Неправильная дата!"
OP_SUCCESS_MSG = "Добавлено"

incomes = []
costs = []


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
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    parts = maybe_dt.split("-")
    if len(parts) != 3:
        return None

    day_str, month_str, year_str = parts

    if len(day_str) != 2 or len(month_str) != 2 or len(year_str) != 4:
        return None

    if not day_str.isdigit() or not month_str.isdigit() or not year_str.isdigit():
        return None

    day = int(day_str)
    month = int(month_str)
    year = int(year_str)

    if month < 1 or month > 12:
        return None

    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    max_day = days_in_month[month - 1]
    if month == 2 and is_leap_year(year):
        max_day = 29

    if day < 1 or day > max_day:
        return None

    return day, month, year


def is_valid_number(number_str: str) -> bool:
    if number_str == "":
        return False

    normalized = number_str.replace(",", ".")

    if normalized.count(".") > 1:
        return False

    parts = normalized.split(".")

    if len(parts) == 1:
        return parts[0].isdigit()

    if len(parts) == 2:
        left, right = parts
        if left == "" or right == "":
            return False
        return left.isdigit() and right.isdigit()

    return False


def parse_number(number_str: str) -> float:
    normalized = number_str.replace(",", ".")
    if "." in normalized:
        left, right = normalized.split(".")
        return int(left) + int(right) / (10 ** len(right))
    return float(int(normalized))


def date_to_number(date_tuple: tuple[int, int, int]) -> int:
    day, month, year = date_tuple
    return year * 10000 + month * 100 + day


def amount_to_text(amount: float) -> str:
    if amount == int(amount):
        return str(int(amount))
    return str(amount)


def income_handler(amount: float, income_date: str) -> str:
    parsed_date = extract_date(income_date)
    if parsed_date is None:
        return INCORRECT_DATE_MSG

    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    incomes.append((amount, parsed_date))
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    parsed_date = extract_date(income_date)
    if parsed_date is None:
        return INCORRECT_DATE_MSG

    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    costs.append((category_name, amount, parsed_date))
    return OP_SUCCESS_MSG


def stats_handler(report_date: str) -> str:
    parsed_report_date = extract_date(report_date)
    if parsed_report_date is None:
        return INCORRECT_DATE_MSG

    report_day, report_month, report_year = parsed_report_date
    report_number = date_to_number(parsed_report_date)

    total_income = 0.0
    total_cost = 0.0
    month_income = 0.0
    month_cost = 0.0
    categories = {}

    for amount, income_date in incomes:
        income_day, income_month, income_year = income_date
        income_number = date_to_number(income_date)

        if income_number <= report_number:
            total_income += amount

        if (
            income_year == report_year
            and income_month == report_month
            and income_day <= report_day
        ):
            month_income += amount

    for category, amount, cost_date in costs:
        cost_day, cost_month, cost_year = cost_date
        cost_number = date_to_number(cost_date)

        if cost_number <= report_number:
            total_cost += amount

        if (
            cost_year == report_year
            and cost_month == report_month
            and cost_day <= report_day
        ):
            month_cost += amount
            if category in categories:
                categories[category] += amount
            else:
                categories[category] = amount

    capital = total_income - total_cost
    difference = month_income - month_cost

    lines = []
    lines.append(f"Ваша статистика по состоянию на {report_date}:")
    lines.append(f"Суммарный капитал: {capital:.2f} рублей")

    if difference >= 0:
        lines.append(f"В этом месяце прибыль составила {difference:.2f} рублей")
    else:
        lines.append(f"В этом месяце убыток составил {-difference:.2f} рублей")

    lines.append(f"Доходы: {month_income:.2f} рублей")
    lines.append(f"Расходы: {month_cost:.2f} рублей")
    lines.append("Детализация (категория: сумма):")

    sorted_categories = sorted(categories)

    for i in range(len(sorted_categories)):
        category = sorted_categories[i]
        lines.append(f"{i + 1}. {category}: {amount_to_text(categories[category])}")

    return "\n".join(lines)


def main() -> None:
    """Ваш код здесь"""
    while True:
        line = input().strip()

        if line == "":
            print(UNKNOWN_COMMAND_MSG)
            continue

        parts = line.split()
        command = parts[0]

        if command == "income":
            if len(parts) != 3:
                print(UNKNOWN_COMMAND_MSG)
                continue

            amount_str = parts[1]
            date_str = parts[2]

            if not is_valid_number(amount_str):
                print(UNKNOWN_COMMAND_MSG)
                continue

            amount = parse_number(amount_str)
            print(income_handler(amount, date_str))

        elif command == "cost":
            if len(parts) != 4:
                print(UNKNOWN_COMMAND_MSG)
                continue

            category_name = parts[1]
            amount_str = parts[2]
            date_str = parts[3]

            if not is_valid_number(amount_str):
                print(UNKNOWN_COMMAND_MSG)
                continue

            amount = parse_number(amount_str)
            print(cost_handler(category_name, amount, date_str))

        elif command == "stats":
            if len(parts) != 2:
                print(UNKNOWN_COMMAND_MSG)
                continue

            date_str = parts[1]
            print(stats_handler(date_str))

        else:
            print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()
