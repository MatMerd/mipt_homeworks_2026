UNKNOWN_COMMAND_MSG = "Неизвестная команда!"
NONPOSITIVE_VALUE_MSG = "Значение должно быть больше нуля!"
INCORRECT_DATE_MSG = "Неправильная дата!"
OP_SUCCESS_MSG = "Добавлено"
LOSS = "убыток составил"
PROFIT = "прибыль составила"

incomes = dict()
costs = dict()

days_to_months = {
    1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31
}


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    return (year % 4 == 0 and year % 100 != 0) or (year % 100 == 0 and year % 400 == 0)


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: tuple формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    day, month, year = [int(i) for i in maybe_dt.split('-')]
    if 1 <= day <= days_to_months[month] and 1 <= month <= 12:
        return (day, month, year)
    return None


def get_correct_float(my_float: str):
    return float(my_float.replace(",", "."))


def get_capital() -> float:
    """Вычисляет суммарный капитал по всем данным"""
    capital = 0.0
    for _, income in incomes.items():
        capital += income
    for _, categories in costs.items():
        for _, cost in categories.items():
            capital -= cost
    return capital


def main() -> None:
    while True:
        command = input().strip().split()
        if not command:
            continue

        if command[0] == "income" and len(command) == 3:
            amount = get_correct_float(command[1])
            if amount <= 0:
                print(NONPOSITIVE_VALUE_MSG)
                continue

            data = extract_date(command[2])
            if data is None:
                print(INCORRECT_DATE_MSG)
                continue

            date_str = command[2]
            if date_str in income:
                income[date_str] += amount
            else:
                income[date_str] = amount
            print(OP_SUCCESS_MSG)
        elif command[0] == "cost" and len(command) == 4:
            category_name = command[1]

            amount = get_correct_float(command[2])
            if amount <= 0:
                print(NONPOSITIVE_VALUE_MSG)
                continue

            data = extract_date(command[3])
            if data is None:
                print(INCORRECT_DATE_MSG)
                continue

            date_str = command[3]
            if date_str not in costs:
                costs[date_str] = {}

            if category_name in costs[date_str]:
                costs[date_str][category_name] += amount
            else:
                costs[date_str][category_name] = amount
            print(OP_SUCCESS_MSG)
        elif command[0] == "stats" and len(command) == 2:
            date_tuple = extract_date(command[1])
            if date_tuple is None:
                print(INCORRECT_DATE_MSG)
                continue

            _, target_month, target_year = date_tuple
            date_str = command[1]

            month_incomes = 0.0
            for date, income in income.items():
                _, month, year = extract_date(date)
                if year == target_year and month == target_month:
                    month_incomes += income

            month_costs = 0.0
            category_costs = {}
            for cost_date, categories in costs.items():
                _, month, year = extract_date(cost_date)
                if year == target_year and month == target_month:
                    for category, cost in categories.items():
                        month_costs += cost
                        category_costs[category] = category_costs.get(category, 0.0) + cost

            changes = month_incomes - month_costs
            loss_or_profit = PROFIT if changes >= 0 else LOSS
            abs_changes = abs(changes)
            capital = get_capital()

            print(f"Ваша статистика по состоянию на {date_str}:")
            print(f"Суммарный капитал: {capital:.2f} рублей")
            print(f"В этом месяце {loss_or_profit} {abs_changes:.2f} рублей")
            print(f"Доходы: {month_incomes:.2f} рублей")
            print(f"Расходы: {month_costs:.2f} рублей\n")
            print("Детализация (категория: сумма):")
            if not category_costs:
                continue
            sorted_categories = sorted(category_costs.items(), key=lambda x: x[0])
            for i, (category, cost) in enumerate(sorted_categories, 1):
                if cost == int(cost):
                    print(f"{i}. {category}: {int(cost)}")
                else:
                    print(f"{i}. {category}: {cost:.2f}")
        else:
            print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()