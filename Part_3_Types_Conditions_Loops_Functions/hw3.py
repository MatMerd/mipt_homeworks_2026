#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be greater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"


def is_leap_year(year: int) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    parts = maybe_dt.split("-")
    if len(parts) != 3:
        return None

    for part in parts:
        if not part.isdigit():
            return None

    day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
    if year < 1 or month < 1 or month > 12 or day < 1:
        return None

    days_in_month = [31, 29 if is_leap_year(year) else 28, 31, 30, 31, 30,
                     31, 31, 30, 31, 30, 31]

    if day > days_in_month[month - 1]:
        return None

    return (day, month, year)



def income_handler(parts: list, incomes: list) -> None:
    if len(parts) != 3:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount_input = parts[1]
    date = parts[2]

    amount = parse_amount(amount_input)
    if amount is None or amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return

    date_tuple = extract_date(date)
    if date_tuple is None:
        print(INCORRECT_DATE_MSG)
        return

    incomes.append((amount, date_tuple))
    print(OP_SUCCESS_MSG)

def cost_handler(parts: list, costs: list) -> None:
    if len(parts) != 4:
        print(UNKNOWN_COMMAND_MSG)
        return

    category = parts[1]
    amount_input = parts[2]
    date = parts[3]

    if not category or " " in category or "," in category or "." in category:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount = parse_amount(amount_input)
    if amount is None or amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return

    date_tuple = extract_date(date)
    if date_tuple is None:
        print(INCORRECT_DATE_MSG)
        return

    costs.append((category, amount, date_tuple))
    print(OP_SUCCESS_MSG)


def stats_handler(parts: list, incomes: list, costs: list) -> None:
    if len(parts) != 2:
        print(UNKNOWN_COMMAND_MSG)
        return

    date = parts[1]
    date_tuple = extract_date(date)
    if date_tuple is None:
        print(INCORRECT_DATE_MSG)
        return

    stats_day, stats_month, stats_year = date_tuple
    total_capital = 0.0
    for amount, (day, month, year) in incomes:
        if (year < stats_year) or (year == stats_year and month < stats_month) or (year == stats_year and month == stats_month and day <= stats_day):
            total_capital += amount

    for _, amount, (day, month, year) in costs:
        if (year < stats_year) or (year == stats_year and month < stats_month) or (year == stats_year and month == stats_month and day <= stats_day):
            total_capital -= amount

    month_incomes = 0.0
    month_by_category = {}

    for amount, (day, month, year) in incomes:
        if year == stats_year and month == stats_month and day <= stats_day:
            month_incomes += amount

    for category, amount, (day, month, year) in costs:
        if year == stats_year and month == stats_month and day <= stats_day:
            month_by_category[category] = month_by_category.get(category, 0.0) + amount

    month_total_costs = sum(month_by_category.values())
    month_result = month_incomes - month_total_costs

    print(f"Ваша статистика по состоянию на {date}:")
    print(f"Суммарный капитал: {total_capital:.2f} рублей")

    if month_result >= 0:
        print(f"В этом месяце прибыль составила {month_result:.2f} рублей")
    else:
        print(f"В этом месяце убыток составил {abs(month_result):.2f} рублей")

    print(f"Доходы: {month_incomes:.2f} рублей")
    print(f"Расходы: {month_total_costs:.2f} рублей")
    print("Детализация (категория: сумма):")

    if month_by_category:
        sorted_categories = sorted(month_by_category.items())
        for i, (category, amount) in enumerate(sorted_categories, 1):
            if amount.is_integer():
                print(f"{i}. {category}: {int(amount)}")
            else:
                print(f"{i}. {category}: {amount}")
    else:
        print()


def parse_amount(amount_input: str) -> float | None:
    amount = amount_input.replace(",", ".")

    for i, char in enumerate(amount):
        if i == 0 and char == "-":
            continue
        if char != "." and not char.isdigit():
            return None
    if amount.count(".") > 1:
        return None

    if "." in amount:
        parts = amount.split(".")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            return None
        if not parts[1].isdigit():
            return None
    return float(amount)


def main() -> None:
    incomes = []
    costs = []

    while True:
        try:
            command_line = input().strip()
        except EOFError:
            break

        if not command_line:
            continue

        parts = command_line.split()
        command = parts[0]

        if command == "income":
            income_handler(parts, incomes)
        elif command == "cost":
            cost_handler(parts, costs)
        elif command == "stats":
            stats_handler(parts, incomes, costs)
        else:
            print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()
