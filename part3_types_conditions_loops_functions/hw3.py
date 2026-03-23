#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

INCOME_QUERY_LENGTH = 3
COST_QUERY_LENGTH = 4
COST_CATEGORY_QUERY_LENGTH = 2
STATS_QUERY_LENGTH = 2

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("SomeCategory", "SomeOtherCategory"),
}

income_storage: dict[tuple[int, int, int], float] = {}
cost_storage: dict[tuple[int, int, int], float] = {}
category_storage: dict[tuple[int, int, int], dict[str, float]] = {}


def is_leap_year(year: int) -> bool:
    if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
        return True
    return False


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    if len(maybe_dt) != 10 or maybe_dt[2] != "-" or maybe_dt[5] != "-":
        return None
    maybe_dt = maybe_dt.split("-")
    if len(maybe_dt) != 3:
        return None

    day, month, year = maybe_dt[0], maybe_dt[1], maybe_dt[2]

    if not day.isdigit() or not month.isdigit() or not year.isdigit():
        return None

    day, month, year = int(day), int(month), int(year)

    days_in_months = {
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
        12: 31,
    }

    if is_leap_year(year):
        days_in_months[2] = 29

    if month > 12 or day > days_in_months[month] or day == 0:
        return None

    return day, month, year


def extract_amount(maybe_amount: str) -> float | None:
    is_negative = 1
    if maybe_amount[0] == "-":
        is_negative = -1
        maybe_amount = maybe_amount[1:]

    maybe_amount = maybe_amount.replace(",", ".").split(".")
    if len(maybe_amount) > 2 or len(maybe_amount) == 0:
        return None
    for i in maybe_amount:
        if not i.isdigit():
            return None
    amount = ".".join(maybe_amount)
    return float(amount) * is_negative


def extract_category(maybe_category: str) -> str | None:
    maybe_category = maybe_category.split("::")
    if maybe_category[0] in EXPENSE_CATEGORIES and maybe_category[1] in EXPENSE_CATEGORIES[maybe_category[0]]:
        return maybe_category[1]
    else:
        return None


def process_income(command: list) -> None:
    if len(command) != INCOME_QUERY_LENGTH:
        print(UNKNOWN_COMMAND_MSG)
    else:
        amount = extract_amount(command[1])
        date = extract_date(command[2])
        if amount <= 0:
            print(NONPOSITIVE_VALUE_MSG)
        elif date is None:
            print(INCORRECT_DATE_MSG)
        else:
            print(income_handler(amount, date))


def income_handler(amount: float, income_date: tuple[int, int, int]) -> str:
    income_storage.setdefault(income_date, 0)
    income_storage[income_date] += amount
    return OP_SUCCESS_MSG


def process_cost(command: list) -> None:
    if len(command) != COST_QUERY_LENGTH and len(command) != COST_CATEGORY_QUERY_LENGTH:
        print(UNKNOWN_COMMAND_MSG)
    else:
        if len(command) == 2:
            if command[1] == "categories":
                cost_categories_handler()
            else:
                print(UNKNOWN_COMMAND_MSG)
        else:
            category_name = extract_category(command[1])
            amount = extract_amount(command[2])
            date = extract_date(command[3])
            if category_name is None:
                print(NOT_EXISTS_CATEGORY)
            elif amount <= 0:
                print(NONPOSITIVE_VALUE_MSG)
            elif date is None:
                print(INCORRECT_DATE_MSG)
            else:
                print(cost_handler(category_name, amount, date))


def cost_handler(category_name: str, amount: float, income_date: tuple[int, int, int]) -> str:
    cost_storage.setdefault(income_date, 0)
    cost_storage[income_date] += amount

    category_storage.setdefault(income_date, {})
    category_storage[income_date].setdefault(category_name, 0)
    category_storage[income_date][category_name] += amount
    return OP_SUCCESS_MSG


def cost_categories_handler() -> None:
    print(EXPENSE_CATEGORIES)


def is_before(processing_date: tuple[int, int, int], date: tuple[int, int, int]) -> bool:
    day, month, year = date
    processing_day, processing_month, processing_year = processing_date
    if processing_year < processing_day:
        return True
    elif processing_year == year:
        if processing_month < month:
            return True
        elif month == processing_month:
            if processing_day <= day:
                return True
    return False


def is_within_month(processing_date, date):
    if (processing_date[1], processing_date[2]) == (date[1], date[2]):
        return True
    return False


def calculate_stats(date: tuple[int, int, int]) -> tuple[float, float, float, dict[str, float]]:
    total_amount = 0
    month_income = 0
    month_cost = 0
    category_costs = {}
    for processing_date in income_storage:
        if is_before(processing_date, date):
            total_amount += income_storage[processing_date]
            if is_within_month(processing_date, date):
                month_income += income_storage[processing_date]

    for processing_date in cost_storage:
        if is_within_month(processing_date, date):
            month_cost += cost_storage[processing_date]
            for category_name in category_storage[processing_date]:
                category_costs.setdefault(category_name, 0)
                category_costs[category_name] += category_storage[processing_date][category_name]

    return total_amount, month_income, month_cost, category_costs


def build_stats(stats: tuple[float, float, float, dict[str, float]], date: tuple[int, int, int]) -> str:
    total_amount, month_income, month_cost, category_costs = stats
    day, month, year = date
    status = "loss" if month_income - month_cost < 0 else "profit"

    result = f"Your statistics as of {day:0>2}-{month:0>2}-{year:0>4}:\n"
    result += f"Total capital: {total_amount:.2f} rubles\n"
    result += f"This month, the {status} amounted to {month_income - month_cost:.2f} rubles.\n"
    result += f"Income: {month_income:.2f} rubles\n"
    result += f"Expenses: {month_cost:.2f} rubles\n"
    result += f"\n"
    result += f"Details (category: amount):\n"
    index = 1
    for category_name, amount in category_costs.items():
        result += f"{index}. {category_name}: {amount:.2f} rubles\n"
        index += 1
    return result


def process_stats(command: list) -> None:
    if len(command) != STATS_QUERY_LENGTH:
        print(UNKNOWN_COMMAND_MSG)
    else:
        date = extract_date(command[1])
        if date is None:
            print(INCORRECT_DATE_MSG)
        else:
            stats = calculate_stats(date)
            print(build_stats(stats, date))


def stats_handler(report_date: str) -> str:
    return f"Statistic for {report_date}"


def handle_command(line: str) -> None:
    command = line.split(" ")
    if len(command) == 0:
        print(UNKNOWN_COMMAND_MSG)

    if command[0] == "income":
        process_income(command)

    elif command[0] == "cost":
        process_cost(command)

    elif command[0] == "stats":
        process_stats(command)

    else:
        print(UNKNOWN_COMMAND_MSG)


def main() -> None:
    line = input()
    while line:
        if not line:
            continue

        handle_command(line)

        line = input()


if __name__ == "__main__":
    main()