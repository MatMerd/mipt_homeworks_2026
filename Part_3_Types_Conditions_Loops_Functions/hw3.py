#!/usr/bin/env python
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
    if year % 4 == 0 and year % 100 != 0:
        return True
    if year % 100 == 0:
        return year % 400 == 0
    return False


k2 = 2
k3 = 3
k4 = 4
k12 = 12


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """

    string = maybe_dt.split("-")

    if len(string) != k3:
        return None

    day, month, year = string
    for s in day, month, year:
        if not s.isdigit():
            return None

    if (len(day), len(month), len(year)) != (k2, k2, k4):
        return None

    day_i, month_i, year_i = map(int, maybe_dt.split("-"))
    if not (1 <= month_i <= k12):
        return None
    days_in_moth = [31, 29 if is_leap_year(year_i) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if not (1 <= day_i <= days_in_moth[month_i - 1]):
        return None

    return day_i, month_i, year_i


def is_valid_number(maybe_num: str) -> bool:
    maybe_num = maybe_num.replace(",", ".")
    if maybe_num.count(".") > 1:
        return False

    maybe_num = maybe_num.removeprefix("-")

    if maybe_num == "":
        return False

    if "." in maybe_num:
        left, right = maybe_num.split(".", 1)
        if left == "" and right == "":
            return False
        if left != "" and not left.isdigit():
            return False
        return not (right != "" and not right.isdigit())

    return maybe_num.isdigit()


def main() -> None:  # noqa: PLR0912, C901, PLR0915
    """Ваш код здесь"""
    records: dict[int | str, list[tuple[float, int, int, int]]] = {}

    for line in open(0):  # noqa: SIM115
        command = line.split()
        if not (command):
            print(UNKNOWN_COMMAND_MSG)
            continue

        if command[0] == "income":
            if len(command) != k3:
                print(UNKNOWN_COMMAND_MSG)  # noqa: T201
                continue
            amount = command[1].replace(",", ".")
            if not is_valid_number(amount):
                print(UNKNOWN_COMMAND_MSG)
                continue
            date = extract_date(command[2])
            if not (date):
                print(INCORRECT_DATE_MSG)  # noqa: T201
                continue
            withdraw = float(amount)
            day, month, year = date
            if withdraw <= 0:
                print(NONPOSITIVE_VALUE_MSG)  # noqa: T201
                continue
            records[0] = [*records.get(0, []), (withdraw, day, month, year)]
            print(OP_SUCCESS_MSG)  # noqa: T201

        elif command[0] == "cost":
            if len(command) != k4:
                print(UNKNOWN_COMMAND_MSG)  # noqa: T201
                continue
            amount = command[2].replace(",", ".")
            if not is_valid_number(amount):
                print(UNKNOWN_COMMAND_MSG)  # noqa: T201
                continue
            date = extract_date(command[3])
            if not (date):
                print(INCORRECT_DATE_MSG)  # noqa: T201
                continue
            name = command[1]
            if "." in name or "," in name:
                print(UNKNOWN_COMMAND_MSG)  # noqa: T201
                continue

            withdraw = float(amount)
            day, month, year = date
            if withdraw <= 0:
                print(NONPOSITIVE_VALUE_MSG)  # noqa: T201
                continue
            records[name] = [*records.get(name, []), (withdraw, day, month, year)]
            print(OP_SUCCESS_MSG)  # noqa: T201

        elif command[0] == "stats":
            if len(command) != k2:
                print(UNKNOWN_COMMAND_MSG)  # noqa: T201
                continue
            date = extract_date(command[1])
            if not (date):
                print(INCORRECT_DATE_MSG)  # noqa: T201
                continue
            print(f"Ваша статистика по состоянию на {command[1]}:")  # noqa: T201
            total_capital = 0.0
            current_income = 0.0
            current_lose = 0.0
            details: dict[str, float] = {}
            target_day, target_month, target_year = date
            target_date = (target_year, target_month, target_day)

            for record_name in records:
                if record_name == 0:
                    for income, day, month, year in records.get(0, []):
                        if (year, month, day) <= target_date:
                            total_capital += income
                        if year == target_year and month == target_month and day <= target_day:
                            current_income += income
                else:
                    category_total = 0.0
                    for withdraw, day, month, year in records.get(record_name, []):
                        if (year, month, day) <= target_date:
                            total_capital -= withdraw
                        if year == target_year and month == target_month and day <= target_day:
                            current_lose += withdraw
                            category_total += withdraw
                    if isinstance(record_name, str) and category_total > 0:
                        details[record_name] = category_total
            print(f"Суммарный капитал: {total_capital:.2f} рублей")  # noqa: T201
            if current_income >= current_lose:
                delta = current_income - current_lose
                print(f"В этом месяце прибыль составила {delta:.2f} рублей")  # noqa: T201, RUF001
            if current_income < current_lose:
                delta = -current_income + current_lose
                print(f"В этом месяце убыток составил {delta:.2f} рублей")  # noqa: T201, RUF001
            print(f"Доходы: {current_income:.2f} рублей")  # noqa: T201
            print(f"Расходы: {current_lose:.2f} рублей")  # noqa: T201
            print()  # noqa: T201
            print("Детализация (категория: сумма):")  # noqa: T201
            for num, i in enumerate(sorted(details.keys())):
                value = details[i]
                value_text = str(int(value)) if value.is_integer() else f"{value:.2f}"
                print(f"{num + 1}. {i}: {value_text}")  # noqa: T201
        else:
            print(UNKNOWN_COMMAND_MSG)  # noqa: T201


if __name__ == "__main__":
    main()
