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
        if year % 400 == 0:
            return True
        return False
    return False

def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """

    str = maybe_dt.split('-')
    if len(str) != 3:
        return None

    day, month, year = str
    for s in day, month, year:
        if not s.isdigit():
            return None


    if not(len(day) == 2 and len(month) == 2 and len(year) == 4):
        return None

    day, month, year = map(int, maybe_dt.split('-'))
    if not(1 <= month <= 12):
        return None
    days_in_moth = [31, 29 if is_leap_year(year) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if not(1 <= day <= days_in_moth[month - 1]):
        return None

    return day, month, year


def is_valid_number(maybe_num: str) -> bool:
    maybe_num = maybe_num.replace(',', '.')
    if maybe_num.count('.') > 1:
        return False

    if maybe_num.startswith('-'):
        maybe_num = maybe_num[1:]

    if maybe_num == "":
        return False

    if '.' in maybe_num:
        left, right = maybe_num.split('.', 1)
        if left == "" and right == "":
            return False
        if left != "" and not left.isdigit():
            return False
        if right != "" and not right.isdigit():
            return False
        return True

    return maybe_num.isdigit()




def main() -> None:
    """Ваш код здесь"""
    records = {}

    for line in open(0):
        command = line.split()
        if not(command):
            print(UNKNOWN_COMMAND_MSG)
            continue

        if (command[0] == 'income'):
            if len(command) != 3:
                print(UNKNOWN_COMMAND_MSG)
                continue
            amount = command[1].replace(',', '.')
            if not is_valid_number(amount):
                print(UNKNOWN_COMMAND_MSG)
                continue
            date = extract_date(command[2])
            if not(date):
                print(INCORRECT_DATE_MSG)
                continue
            withdraw = float(amount)
            day, month, year = date
            if (withdraw <= 0):
                print(NONPOSITIVE_VALUE_MSG)
                continue
            records[0] = records.get(0, []) + [(withdraw, day, month, year)]
            print(OP_SUCCESS_MSG)

        elif (command[0] == 'cost'):
            if len(command) != 4:
                print(UNKNOWN_COMMAND_MSG)
                continue
            amount = command[2].replace(',', '.')
            if not is_valid_number(amount):
                print(UNKNOWN_COMMAND_MSG)
                continue
            date = extract_date(command[3])
            if not(date):
                print(INCORRECT_DATE_MSG)
                continue
            name = command[1]
            if "." in name or "," in name:
                print(UNKNOWN_COMMAND_MSG)
                continue

            withdraw = float(amount)
            day, month, year = date
            if (withdraw <= 0):
                print(NONPOSITIVE_VALUE_MSG)
                continue
            records[name] = records.get(name, []) + [(withdraw, day, month, year)]
            print(OP_SUCCESS_MSG)

        elif (command[0] == 'stats'):
            if len(command) != 2:
                print(UNKNOWN_COMMAND_MSG)
                continue
            date = extract_date(command[1])
            if not(date):
                print(INCORRECT_DATE_MSG)
                continue
            print(f"Ваша статистика по состоянию на {command[1]}:")
            total_capital = 0
            current_income = 0
            current_lose = 0
            details = {}
            target_day, target_month, target_year = date
            target_date = (target_year, target_month, target_day)

            for name in records.keys():
                if name == 0:
                    for income, day, month, year in records.get(0, []):
                        if (year, month, day) <= target_date:
                            total_capital += income
                        if year == target_year and month == target_month and day <= target_day:
                            current_income += income
                else:
                    category_total = 0
                    for withdraw, day, month, year in records.get(name, []):
                        if (year, month, day) <= target_date:
                            total_capital -= withdraw
                        if year == target_year and month == target_month and day <= target_day:
                            current_lose += withdraw
                            category_total += withdraw
                    if category_total > 0:
                        details[name] = category_total
            print(f"Суммарный капитал: {total_capital:.2f} рублей")
            if (current_income >= current_lose):
                delta = current_income - current_lose
                print(f"В этом месяце прибыль составила {delta:.2f} рублей")
            if (current_income < current_lose):
                delta = - current_income + current_lose
                print(f"В этом месяце убыток составил {delta:.2f} рублей")
            print(f"Доходы: {current_income:.2f} рублей")
            print(f"Расходы: {current_lose:.2f} рублей")
            print()
            print("Детализация (категория: сумма):")
            for num, i in enumerate(sorted(details.keys())):
                value = details[i]
                value_text = str(int(value)) if value.is_integer() else f"{value:.2f}"
                print(f"{num + 1}. {i}: {value_text}")
        else:
            print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()
