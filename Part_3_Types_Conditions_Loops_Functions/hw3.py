#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"
EXPECTED_INCOME_ARGS = 2
EXPECTED_COST_ARGS = 3
EXPECTED_STATS_ARGS = 1
DATE_PARTS_COUNT = 3
MIN_MONTH = 1
MAX_MONTH = 12
MIN_DAY = 1


class Data:
    def __init__(self):
        self._cost = {}
        self._income = {}

    def add_income(self, date: str, amount: float):
        if date not in self._income:
            self._income[date] = 0
        self._income[date] += amount

    def add_cost(self, date: str, category: str, amount: float):
        if date not in self._cost:
            self._cost[date] = {}
        if category not in self._cost[date]:
            self._cost[date][category] = 0
        self._cost[date][category] += amount

    def get_stats(self, target_date: tuple[int, int, int]):
        target_day, target_month, target_year = target_date

        total_capital = 0
        monthly_income = 0
        monthly_expenses = 0
        monthly_costs_by_category = {}

        for date_str, amount in self._income.items():
            day, month, year = map(int, date_str.split("-"))
            if self._is_before(day, month, year, target_day, target_month, target_year):
                total_capital += amount
                if year == target_year and month == target_month:
                    monthly_income += amount

        for date_str, categories in self._cost.items():
            day, month, year = map(int, date_str.split("-"))
            if self._is_before(day, month, year, target_day, target_month, target_year):
                day_total = sum(categories.values())
                total_capital -= day_total

                if year == target_year and month == target_month:
                    monthly_expenses += day_total
                    for category, cat_amount in categories.items():
                        monthly_costs_by_category[category] = (
                            monthly_costs_by_category.get(category, 0) + cat_amount
                        )

        return {
            "capital": total_capital,
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "categories": monthly_costs_by_category,
        }

    def _is_before(self, day, month, year, t_day, t_month, t_year):
        """Проверяет, что дата <= целевой даты (убирает дублирование логики)"""
        if year < t_year:
            return True
        if year > t_year:
            return False
        if month < t_month:
            return True
        if month > t_month:
            return False
        return day <= t_day


class Handler:
    def __init__(self):
        self.data = Data()
        while True:
            try:
                command_line = input().strip()
                if not command_line:
                    continue
                parts = command_line.split()
                command = parts[0]
                details = parts[1:] if len(parts) > 1 else []
                self.handler(command, details)
            except EOFError:
                break

    def _parse_float(self, value: str) -> float:
        return float(value.replace(",", "."))

    def handler(self, command: str, details: list):
        match command:
            case "income":
                self._income(details)
            case "cost":
                self._cost(details)
            case "stats":
                self._stats(details)
            case _:
                print(UNKNOWN_COMMAND_MSG)

    def _income(self, details: list):
        if len(details) != EXPECTED_INCOME_ARGS:
            print(UNKNOWN_COMMAND_MSG)
            return

        amount_str, date_str = details

        date_tuple = extract_date(date_str)
        if date_tuple is None:
            return

        try:
            amount = self._parse_float(amount_str)
            if amount <= 0:
                print(NONPOSITIVE_VALUE_MSG)
                return
        except ValueError:
            print(UNKNOWN_COMMAND_MSG)
            return

        formatted_date = "-".join(map(str, date_tuple))
        self.data.add_income(formatted_date, amount)
        print(OP_SUCCESS_MSG)

    def _cost(self, details: list):
        if len(details) != EXPECTED_COST_ARGS:
            print(UNKNOWN_COMMAND_MSG)
            return

        category, amount_str, date_str = details

        if not category or " " in category or "." in category or "," in category:
            print(UNKNOWN_COMMAND_MSG)
            return

        date_tuple = extract_date(date_str)
        if date_tuple is None:
            return

        try:
            amount = self._parse_float(amount_str)
            if amount <= 0:
                print(NONPOSITIVE_VALUE_MSG)
                return
        except ValueError:
            print(UNKNOWN_COMMAND_MSG)
            return

        formatted_date = "-".join(map(str, date_tuple))
        self.data.add_cost(formatted_date, category, amount)
        print(OP_SUCCESS_MSG)

    def _stats(self, details: list):
        if len(details) != EXPECTED_STATS_ARGS:
            print(UNKNOWN_COMMAND_MSG)
            return

        date_str = details[0]
        date_tuple = extract_date(date_str)
        if date_tuple is None:
            return

        stats = self.data.get_stats(date_tuple)

        day, month, year = date_tuple
        print(f"Ваша статистика по состоянию на {day:02d}-{month:02d}-{year}:")
        print(f"Суммарный капитал: {stats['capital']:.2f} рублей")

        profit = stats['monthly_income'] - stats['monthly_expenses']
        if profit >= 0:
            print(f"Месячная прибыль составила {profit:.2f} рублей")
        else:
            print(f"Месячный убыток составил {abs(profit):.2f} рублей")

        print(f"Доходы: {stats['monthly_income']:.2f} рублей")
        print(f"Расходы: {stats['monthly_expenses']:.2f} рублей")
        print()
        print("Детализация (категория: сумма):")

        if stats['categories']:
            sorted_categories = sorted(stats['categories'].items())
            for i, (category, amount) in enumerate(sorted_categories, 1):
                print(f"{i}. {category}: {amount:.2f}")
        else:
            print()


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).
    """
    by_four = year % 4 == 0
    by_hundred = year % 100 == 0
    by_four_hundred = year % 400 == 0
    return (by_four and not by_hundred) or by_four_hundred


def _get_days_in_month(month: int, year: int) -> int:
    """Количество дней в месяце"""
    days = [31, 29 if is_leap_year(year) else 28, 31, 30, 31, 30,
            31, 31, 30, 31, 30, 31]
    return days[month - 1]


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.
    """
    try:
        parts = maybe_dt.split("-")
        if len(parts) != DATE_PARTS_COUNT:
            print(INCORRECT_DATE_MSG)
            return None

        day, month, year = map(int, parts)

        if not (MIN_MONTH <= month <= MAX_MONTH):
            print(INCORRECT_DATE_MSG)
            return None

        if not (MIN_DAY <= day <= _get_days_in_month(month, year)):
            print(INCORRECT_DATE_MSG)
            return None

        return (day, month, year)

    except (ValueError, IndexError):
        print(INCORRECT_DATE_MSG)
        return None


def main() -> None:
    Handler()


if __name__ == "__main__":
    main()
