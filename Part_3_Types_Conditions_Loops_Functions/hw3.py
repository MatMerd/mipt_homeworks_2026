UNKNOWN_COMMAND_MSG = "Неизвестная команда!"
NONPOSITIVE_VALUE_MSG = "Значение должно быть больше нуля!"
INCORRECT_DATE_MSG = "Неправильная дата!"
OP_SUCCESS_MSG = "Добавлено"


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


def extract_amount(amount_string: str) -> float | None:
    if amount_string == "":
        return None

    sign = 1
    index = 0

    if amount_string[0] == "-":
        sign = -1
        index = 1
    elif amount_string[0] == "+":
        index = 1

    if index == len(amount_string):
        return None

    int_part = 0
    frac_part = 0
    frac_div = 1

    seen_separator = False
    digits_before = 0
    digits_after = 0

    while index < len(amount_string):
        ch = amount_string[index]

        if "0" <= ch <= "9":
            digit = ord(ch) - ord("0")
            if not seen_separator:
                int_part = int_part * 10 + digit
                digits_before += 1
            else:
                frac_part = frac_part * 10 + digit
                frac_div *= 10
                digits_after += 1
        elif ch == "." or ch == ",":
            if seen_separator:
                return None
            seen_separator = True
        else:
            return None

        index += 1

    if digits_before == 0:
        return None

    if seen_separator and digits_after == 0:
        return None

    return sign * (int_part + (frac_part / frac_div))


def is_valid_category(category_name: str) -> bool:
    for ch in category_name:
        if ch == " " or ch == "." or ch == ",":
            return False

    return category_name != ""


def date_not_later(day1: int, month1: int, year1: int, day2: int, month2: int, year2: int) -> bool:
    return (year1, month1, day1) <= (year2, month2, day2)


def format_detail_amount(value: float) -> str:
    result = f"{value:.10f}".rstrip("0").rstrip(".")
    return result or "0"


def print_stats(stats_date: tuple[int, int, int], incomes: list, costs: list):
    day, month, year = stats_date

    total_capital = 0.0
    month_income = 0.0
    month_cost = 0.0
    category_sums = {}

    for amount, inc_day, inc_month, inc_year in incomes:
        if date_not_later(inc_day, inc_month, inc_year, day, month, year):
            total_capital += amount
            if inc_month == month and inc_year == year:
                month_income += amount

    for category, amount, cost_day, cost_month, cost_year in costs:
        if date_not_later(cost_day, cost_month, cost_year, day, month, year):
            total_capital -= amount
            if cost_month == month and cost_year == year:
                month_cost += amount
                if category not in category_sums:
                    category_sums[category] = 0.0
                category_sums[category] += amount

    delta = month_income - month_cost

    print(f"Ваша статистика по состоянию на {day:02d}-{month:02d}-{year:04d}:")
    print(f"Суммарный капитал: {total_capital:.2f} рублей")

    if delta >= 0:
        print(f"В этом месяце прибыль составила {delta:.2f} рублей")
    else:
        print(f"В этом месяце убыток составил {(-delta):.2f} рублей")

    print(f"Доходы: {month_income:.2f} рублей")
    print(f"Расходы: {month_cost:.2f} рублей")
    print()
    print("Детализация (категория: сумма):")

    sorted_categories = sorted(category_sums.keys())
    for index in range(len(sorted_categories)):
        category = sorted_categories[index]
        print(f"{index + 1}. {category}: {format_detail_amount(category_sums[category])}")




def main() -> None:
    """Ваш код здесь"""
    incomes = []
    costs = []

    for line in open(0):
        line = line.strip()

        if line == "":
            print(UNKNOWN_COMMAND_MSG)
            continue

        parts = line.split()
        command = parts[0]

        if command == "income":
            if len(parts) != 3:
                print(UNKNOWN_COMMAND_MSG)
                continue

            amount = extract_amount(parts[1])
            if amount is None or amount <= 0:
                print(NONPOSITIVE_VALUE_MSG)
                continue

            current_date = extract_date(parts[2])
            if current_date is None:
                print(INCORRECT_DATE_MSG)
                continue

            day, month, year = current_date
            incomes.append((amount, day, month, year))
            print(OP_SUCCESS_MSG)

        elif command == "cost":
            if len(parts) != 4:
                print(UNKNOWN_COMMAND_MSG)
                continue

            category_name = parts[1]
            if not is_valid_category(category_name):
                print(UNKNOWN_COMMAND_MSG)
                continue

            amount = extract_amount(parts[2])
            if amount is None or amount <= 0:
                print(NONPOSITIVE_VALUE_MSG)
                continue

            current_date = extract_date(parts[3])
            if current_date is None:
                print(INCORRECT_DATE_MSG)
                continue

            day, month, year = current_date
            costs.append((category_name, amount, day, month, year))
            print(OP_SUCCESS_MSG)

        elif command == "stats":
            if len(parts) != 2:
                print(UNKNOWN_COMMAND_MSG)
                continue

            current_date = extract_date(parts[1])
            if current_date is None:
                print(INCORRECT_DATE_MSG)
                continue

            print_stats(current_date, incomes, costs)

        else:
            print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()
