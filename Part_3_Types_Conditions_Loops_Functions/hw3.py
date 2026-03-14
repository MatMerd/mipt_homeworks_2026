UNKNOWN_COMMAND_MSG = "Неизвестная команда!"
NONPOSITIVE_VALUE_MSG = "Значение должно быть больше нуля!"
INCORRECT_DATE_MSG = "Неправильная дата!"
OP_SUCCESS_MSG = "Добавлено"


def is_leap_year(year: int) -> bool:
    return (year % 400 == 0) or ((year % 4 == 0) and (year % 100 != 0))


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] or None
    """
    data = maybe_dt.split("-")

    if len(data) != 3 or len(data[0]) != 2 or len(data[1]) != 2 or len(data[2]) != 4:
        return None
    if not (data[0].isdigit()) or not (data[1].isdigit()) or not (data[2].isdigit()):
        return None

    data_elems_int = tuple(map(int, data))
    day, month, year = data_elems_int

    if not (1 <= month <= 12):
        return None

    days_in_month = [31, 29 if is_leap_year(year) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if not (1 <= day <= days_in_month[month - 1]):
        return None

    return day, month, year


def is_valid_number(maybe_number: str) -> bool:
    new_num = maybe_number
    if '.' in new_num:
        new_num = new_num.replace(".", "", 1)
    elif "," in new_num:
        new_num = new_num.replace(",", "", 1)

    check_num = new_num[1:] if new_num.startswith("-") else new_num

    if check_num.isdigit():
        if new_num.startswith("-") or check_num.count("0") == len(check_num):
            print(NONPOSITIVE_VALUE_MSG)
            return False
        return True

    print(UNKNOWN_COMMAND_MSG)
    return False


def amount_to_number(maybe_amount: str) -> float | int:
    if is_valid_number(maybe_amount):
        if "," in maybe_amount:
            return float(maybe_amount.replace(",", "."))
        elif "." in maybe_amount:
            return float(maybe_amount)
        else:
            return int(maybe_amount)
    return 0


def add_income(maybe_correct: str) -> tuple[int | float, tuple[int, int, int]] | None:
    string = maybe_correct.split()
    if len(string) != 3:
        print(UNKNOWN_COMMAND_MSG)
        return None

    income, amount, data = string

    success = amount_to_number(amount)
    if not success:
        return None

    data_checked = extract_date(data)
    if not data_checked:
        print(INCORRECT_DATE_MSG)
        return None

    print(OP_SUCCESS_MSG)
    return success, data_checked


def add_cost(maybe_correct: str) -> tuple[str, int | float, tuple[int, int, int]] | None:
    string = maybe_correct.split()
    if len(string) != 4:
        print(UNKNOWN_COMMAND_MSG)
        return None

    cost, category_name, amount, data = string

    success = amount_to_number(amount)
    if not success:
        return None

    data_checked = extract_date(data)
    if not data_checked:
        print(INCORRECT_DATE_MSG)
        return None

    print(OP_SUCCESS_MSG)
    return category_name, success, data_checked


def main() -> None:
    statistics = dict()
    for line in open(0):
        line_arr = line.split()
        if not line_arr:
            print(UNKNOWN_COMMAND_MSG)
            continue
        comand = line_arr[0]
        if "income" == comand:
            result = add_income(line)
            if result is not None:
                amount, date = result

                if date not in statistics:
                    statistics[date] = {"income": 0, "cost": {}}
                statistics[date]["income"] += amount
                continue
            continue

        elif "cost" == comand:
            result = add_cost(line)
            if result is not None:
                category_name, amount, date = result

                if date not in statistics:
                    statistics[date] = {"income": 0.0, "cost": {}}
                if category_name not in statistics[date]["cost"]:
                    statistics[date]["cost"][category_name] = 0.0
                statistics[date]["cost"][category_name] += amount
                continue
            continue

        elif "stats" == comand:
            if len(line_arr) != 2:
                print(UNKNOWN_COMMAND_MSG)
                continue

            arg, date_str = line_arr
            date_tuple = extract_date(date_str)

            if date_tuple is None:
                print(INCORRECT_DATE_MSG)
                continue

            day, month, year = date_tuple

            total_capital = 0.0
            month_income = 0.0
            month_cost = 0.0
            category_stats = {}

            for (d, m, y), data in statistics.items():
                cost_sum = sum(data["cost"].values())

                if (y, m, d) <= (year, month, day):
                    total_capital += data["income"]
                    total_capital -= cost_sum

                if y == year and m == month and d <= day:
                    month_income += data["income"]
                    month_cost += cost_sum
                    for category, val in data["cost"].items():
                        category_stats[category] = category_stats.get(category, 0.0) + val

            delta = month_income - month_cost

            print(f"Ваша статистика по состоянию на {date_str}:")
            print(f"Суммарный капитал: {total_capital:.2f} рублей")

            if delta >= 0:
                print(f"В этом месяце прибыль составила {delta:.2f} рублей")
            else:
                print(f"В этом месяце убыток составил {abs(delta):.2f} рублей")

            print(f"Доходы: {month_income:.2f} рублей")
            print(f"Расходы: {month_cost:.2f} рублей")
            print()
            print("Детализация (категория: сумма):")

            if category_stats:
                for i, category in enumerate(sorted(category_stats), 1):
                    val = category_stats[category]
                    val_out = int(val) if val == int(val) else val
                    print(f"{i}. {category}: {val_out}")
            continue

        else:
            print(UNKNOWN_COMMAND_MSG)
            continue


if __name__ == "__main__":
    main()
