#!/usr/bin/env python

"""# ДЗ №1: Budget manager

В рамках данного домашнего задания Вам предстоит реализовать небольшое консольное приложение для управления личными финансами.

Наш потенциальный пользователь хочет вносить данные о своих доходах и расходах, а также получать по ним статистику:
- месячная прибыль/убыток;
- распределение месячных расходов по статьям;
- суммарный размер капитала на конец месяца.

Необходимо реализовать следующие пользовательские сценарии:

## Добавление дохода

Для добавления дохода необходимо обрабатывать строку вида:
```
income <amount> <date>
```

Допустим, нам прилетел кэшбэк, целых 49 с чем-то рублей!
```
income 49,5 28-02-2026
# или
income 49 28-02-2026
# или
income 49,0 28-02-2026
# или
income 49.0 28-02-2026
```

В ответ печатаем:

```
Добавлено
```

Однако доход не может быть ≤ 0. Если ввели неположительное число, выводим ошибку:
```
Значение должно быть больше нуля!
```

## Добавление расхода

Для добавления расхода необходимо обрабатывать строку вида:
```
cost <category_name> <amount> <date>
```

Вводим
```
cost фастфуд 555,5 28-02-2026
```

Если всё корректно, печатаем ответ:
```
Добавлено
```

Значение расхода не может быть ≤ 0. Если ввели неположительное число, отвечаем:
```
Значение должно быть больше нуля!
```

## Просмотр статистики

Сырые данные никому не нужны, мы хотим видеть insights.

Для вывода статистики необходимо обрабатывать строку вида:

```
stats <date>
```

Вводим:
```
stats 28-02-2026
```

Получаем ответ:
```
Ваша статистика по состоянию на 28-02-2026:
Суммарный капитал: 35000.00 рублей
В этом месяце убыток составил 5000.00 рублей
Доходы: 80000.00 рублей
Расходы: 85000.00 рублей

Детализация (категория: сумма):
1. аренда: 45000
2. подарки: 20000
3. подписки: 10000
4. фастфуд: 10000
```

Вводим
```
stats 15-02-2026
```

Получаем ответ
```
Ваша статистика по состоянию на 15-02-2026:
Суммарный капитал: 50000.00 рублей
В этом месяце прибыль составила 10000.00 рублей
Доходы: 40000.00 рублей
Расходы: 30000.00 рублей

Детализация (категория: сумма):
1. подарки: 10000
2. подписки: 10000
3. фастфуд: 10000
```

Обратите внимание:
* Статьи расходов сортируются по алфавиту.

* Если расходов в периоде не было - просто не печатаем нумерованный спискок, оставляем строчку с двоеточием.

* Следите за "прибыль составила"/"убыток составил"

## Работа с ошибками
В случае неверных данных, в ответ выводим:
* Если введена неизвестная команда или число аргументов нестандартное: "Неизвестная команда!"
* Если ввели доход или расход меньше или равный нулю: "Значение должно быть больше нуля!"
* Если ввели неверную дату (см. принятые ограничения п.4): "Неправильная дата!"
* Если в строке неверное число и неверная дата, то выводим ошибку для крайнего левого аргумента (для числа)


## Принятые ограничения
1) **Сохранение/чтение данных в файл/бд делать не нужно**. Сериализация/десериализация ждёт нас позже. Исходим из факта, что пользователь при каждом запуске начинает с нуля. То есть нулевой капитал и чистая история.
2) **Названия статей расходов (category_name) состоят из одного слова без пробелов, точек и запятых**. Пустая строка и/или пробелы не принимаются.
3) **Помните про даты доходов и расходов**. В тестах данные могут быть по разным месяцам, в статистиках ориентируемся только на текущий месяц. Исключение - суммарный капитал. Его считаем по всем историческим данным до указанного дня.
4) **Для дат проверка строгая**: Учитывайте високосные года, следите за количеством дней в месяце. (Если год делится на 4, но не делится на 100, он високосный. Однако если год делится на 100, он високосный только в том случае, если делится на 400)
5) **На вход принимаем и целые, и вещественные числа**.
6) **Удалять функции `main`, `is_leap_year` и `extract_date` нельзя, менять аргументы тоже.**
7) Импортировать ничего не нужно. Задание нацелено на закрепление работы с циклами, базовыми типами и управляющими конструкциями. datetime использовать тоже запрещается:)
8) Тему исключений мы ещё не прошли, поэтому try except тоже не используем.
"""


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
    return year % 4 == 0 and year % 100 != 0 or year % 400 == 0


def check_date(probable_date: str) -> tuple[int, int, int] | None:
    probable_date = probable_date.strip()
    parts = probable_date.split("-")
    if len(parts) != 3:
        return None
    dd, mm, yyyy = parts
    if not (dd.isdigit() and mm.isdigit() and yyyy.isdigit()):
        return None
    day = int(dd)
    month = int(mm)
    year = int(yyyy)
    if not (1970 <= year <= 9999):
        return None
    if not (1 <= month <= 12):
        return None
    if month in (1, 3, 5, 7, 8, 10, 12):
        max_day = 31
    elif month in (4, 6, 9, 11):
        max_day = 30
    else:
        max_day = 29 if is_leap_year(year) else 28
    if not (1 <= day <= max_day):
        return None
    return day, month, year


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    return check_date(maybe_dt)


class CommandManager:
    def __init__(self) -> None:
        self.operations: list[dict] = []

    def parse_amount(maybe_amount: str) -> float | None:
        s = maybe_amount.strip().replace(",", ".")
        if not s:
            return None
        dot_count = 0
        for ch in s:
            if ch == ".":
                dot_count += 1
                if dot_count > 1:
                    return None
            elif not ch.isdigit():
                return None
        amount = float(s)
        return amount

    def add_income(self, amount_str: str, date_str: str) -> str:
        amount = self.parse_amount(amount_str)
        if amount is None or amount <= 0:
            return NONPOSITIVE_VALUE_MSG
        dt = extract_date(date_str)
        if dt is None:
            return INCORRECT_DATE_MSG
        self.operations.append(
            {"type": "income", "amount": amount, "date": dt, "category": None}
        )
        return OP_SUCCESS_MSG

    def add_cost(self, category: str, amount_str: str, date_str: str) -> str:
        if not category or any(ch in " .," for ch in category):
            return UNKNOWN_COMMAND_MSG
        amount = self.parse_amount(amount_str)
        if amount is None or amount <= 0:
            return NONPOSITIVE_VALUE_MSG
        dt = extract_date(date_str)
        if dt is None:
            return INCORRECT_DATE_MSG
        self.operations.append(
            {"type": "cost", "amount": amount, "date": dt, "category": category}
        )
        return OP_SUCCESS_MSG

    def format_money(value: float) -> str:
        return f"{value:.2f}"

    def format_category_amount(value: float) -> str:
        if abs(value - int(value)) < 10**(-9):
            return str(int(value))
        return f"{value:.2f}"

    def get_stats(self, date_str: str) -> str:
        dt = extract_date(date_str)
        if dt is None:
            return INCORRECT_DATE_MSG
        day, month, year = dt

        total_capital = 0.0
        month_income = 0.0
        month_costs = 0.0
        categories: dict[str, float] = {}

        for op in self.operations:
            op_day, op_month, op_year = op["date"]
            op_date = (op_year, op_month, op_day)
            target_date = (year, month, day)

            if op_date <= target_date:
                if op["type"] == "income":
                    total_capital += op["amount"]
                else:
                    total_capital -= op["amount"]

            if op_year == year and op_month == month and op_day <= day:
                if op["type"] == "income":
                    month_income += op["amount"]
                else:
                    month_costs += op["amount"]
                    cat = op["category"]
                    if cat is not None:
                        categories[cat] = categories.get(cat, 0.0) + op["amount"]

        profit = month_income - month_costs
        if profit >= 0:
            profit_str = (
                f"В этом месяце прибыль составила "
                f"{self.format_money(profit)} рублей"
            )
        else:
            profit_str = (
                f"В этом месяце убыток составил "
                f"{self.format_money(-profit)} рублей"
            )

        lines: list[str] = []
        lines.append(f"Ваша статистика по состоянию на {date_str}:")
        lines.append(
            f"Суммарный капитал: "
            f"{self.format_money(total_capital)} рублей"
        )
        lines.append(profit_str)
        lines.append(
            f"Доходы: {self.format_money(month_income)} рублей"
        )
        lines.append(
            f"Расходы: {self.format_money(month_costs)} рублей"
        )
        lines.append("")
        lines.append("Детализация (категория: сумма):")
        if categories:
            for idx, cat in enumerate(sorted(categories.keys()), start=1):
                lines.append(
                    f"{idx}. {cat}: {self.format_category_amount(categories[cat])}"
                )

        return "\n".join(lines)


def main() -> None:
    manager = CommandManager()

    while True:
        try:
            line = input().strip()
        except EOFError:
            break

        if not line:
            continue

        parts = line.split()
        cmd = parts[0]

        if cmd == "income":
            if len(parts) != 3:
                print(UNKNOWN_COMMAND_MSG)
                continue
            amount_str = parts[1]
            date_str = parts[2]
            result = manager.add_income(amount_str, date_str)
            print(result)

        elif cmd == "cost":
            if len(parts) != 4:
                print(UNKNOWN_COMMAND_MSG)
                continue
            category = parts[1]
            amount_str = parts[2]
            date_str = parts[3]
            result = manager.add_cost(category, amount_str, date_str)
            print(result)

        elif cmd == "stats":
            if len(parts) != 2:
                print(UNKNOWN_COMMAND_MSG)
                continue
            date_str = parts[1]
            result = manager.get_stats(date_str)
            print(result)

        else:
            print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()
