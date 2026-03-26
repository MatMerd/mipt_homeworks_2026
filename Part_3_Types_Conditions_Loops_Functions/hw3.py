#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
INCORRECT_CATEGORY_MSG = "Category not exists!"
OP_SUCCESS_MSG = "Added"
NUMBER_OF_DATE_PARTS = 3
DATE_SEP = "-"
FEBRUARY = 2
CategoryStat = tuple[str, float]
CategoryStats = list[CategoryStat]
StatsResult = tuple[float, float, float, CategoryStats]


def get_expense_categories() -> dict[str, tuple[str, ...]]:
    return {
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

income_transactions: list[tuple[float, str]] = []
cost_transactions: list[tuple[str, float, str]] = []


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    leap = year % 4 == 0 and year % 100 != 0
    return leap or year % 400 == 0


def check_date_format(maybe_dt: str) -> bool:

    if maybe_dt is None:
        return False
    if len(maybe_dt.split(DATE_SEP)) != NUMBER_OF_DATE_PARTS:
        return False
    date_sep_in_front_or_back = maybe_dt[0] == DATE_SEP or maybe_dt[-1] == DATE_SEP
    if "--" in maybe_dt or date_sep_in_front_or_back:
        return False

    return all(char in "0123456789-" for char in maybe_dt)


DAYS_IN_MONTH = (
    31,
    28,
    31,
    30,
    31,
    30,
    31,
    31,
    30,
    31,
    30,
    31,
)


def check_date_bounds(day: int, month: int, year: int) -> bool:
    if month < 1 or month > len(DAYS_IN_MONTH):
        return False

    max_day = DAYS_IN_MONTH[month - 1]
    if month == FEBRUARY and is_leap_year(year):
        max_day = 29

    return 1 <= day <= max_day


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    if not check_date_format(maybe_dt):
        return None

    day, month, year = map(int, maybe_dt.split("-"))

    if not check_date_bounds(day, month, year):
        return None

    return day, month, year


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG
    if extract_date(income_date) is None:
        return INCORRECT_DATE_MSG

    income_transactions.append((amount, income_date))
    return OP_SUCCESS_MSG


CORRECT_PARTS_NUMBER = 2


def is_valid_category(category: str) -> bool:
    if "::" not in category:
        return False

    parts = category.split("::")
    if len(parts) != CORRECT_PARTS_NUMBER:
        return False

    common_category = parts[0]
    target_category = parts[1]

    if common_category not in get_expense_categories():
        return False

    return target_category in get_expense_categories()[common_category]


def cost_categories_handler() -> str:
    lines: list[str] = []

    for common_category, targets in get_expense_categories().items():
        lines.extend(f"{common_category}::{target_category}" for target_category in targets)

    return "\n".join(lines)


def category_error_with_list() -> str:
    return f"{INCORRECT_CATEGORY_MSG}\n{cost_categories_handler()}"


def cost_handler(category: str, amount: float, cost_date: str) -> str:
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG
    if extract_date(cost_date) is None:
        return INCORRECT_DATE_MSG
    if not is_valid_category(category):
        return category_error_with_list()
    cost_transactions.append((category, amount, cost_date))
    return OP_SUCCESS_MSG


def check_year_bonds(first_year: int, second_year: int) -> bool | None:
    if first_year < second_year:
        return True
    if first_year > second_year:
        return False
    return None


def is_not_later(first_date: str, second_date: str) -> bool:
    first = extract_date(first_date)
    second = extract_date(second_date)
    if first is not None and second is not None:
        year_check = check_year_bonds(first[2], second[2])
        if year_check is not None:
            return year_check

        if first[1] < second[1]:
            return True
        if first[1] > second[1]:
            return False

        return first[0] <= second[0]
    return False


def count_capital(date: str) -> float:
    income_transaction_sum = sum(
        income_transaction[0] for income_transaction in income_transactions if is_not_later(income_transaction[1], date)
    )
    loss_transaction_sum = sum(
        loss_transaction[1] for loss_transaction in cost_transactions if is_not_later(loss_transaction[2], date)
    )
    return income_transaction_sum - loss_transaction_sum


def count_loss(date: str) -> float:
    total = float(0)

    for transaction in cost_transactions:
        if is_earlier_than_target_date(transaction[2], date):
            total += transaction[1]

    return total


def count_profit(date: str) -> float:
    total = float(0)

    for transaction in income_transactions:
        if is_earlier_than_target_date(transaction[1], date):
            total += transaction[0]

    return total


def extract_target_category(category: str) -> str:
    return category.split("::")[1]


def extract_category_and_amount(date: str) -> list[tuple[str, float]]:
    categories: dict[str, float] = {}

    for transaction in cost_transactions:
        if is_earlier_than_target_date(transaction[2], date):
            target_category = extract_target_category(transaction[0])

            if target_category not in categories:
                categories[target_category] = float(0)

            categories[target_category] += transaction[1]

    return list(categories.items())


def get_year(date: tuple[int, int, int]) -> int:
    return date[2]


def get_month(date: tuple[int, int, int]) -> int:
    return date[1]


def get_day(date: tuple[int, int, int]) -> int:
    return date[0]


Date = tuple[int, int, int]


def is_same_year(date1: Date, date2: Date) -> bool:
    return get_year(date1) == get_year(date2)


def is_same_month(date1: Date, date2: Date) -> bool:
    return is_same_year(date1, date2) and get_month(date1) == get_month(date2)


def is_not_later_parsed(date1: Date, date2: Date) -> bool:
    if get_year(date1) != get_year(date2):
        return get_year(date1) < get_year(date2)

    if get_month(date1) != get_month(date2):
        return get_month(date1) < get_month(date2)

    return get_day(date1) <= get_day(date2)


def is_earlier_than_target_date(transaction_date: str, target_date: str) -> bool:
    parsed_transaction = extract_date(transaction_date)
    parsed_target = extract_date(target_date)

    if parsed_transaction is None or parsed_target is None:
        return False

    return is_same_month(parsed_transaction, parsed_target) and is_not_later_parsed(parsed_transaction, parsed_target)


def stats_handler(date: str) -> StatsResult:
    parsed_date = extract_date(date)
    if parsed_date is None:
        return 0, 0, 0, []

    category_stats = extract_category_and_amount(date)
    category_stats.sort(key=lambda category: category[0])

    return (
        count_capital(date),
        count_loss(date),
        count_profit(date),
        category_stats,
    )


def check_comma_in_front_or_back(maybe_float: str) -> bool:
    return maybe_float[0] in ",." or maybe_float[-1] in ",."


NUM_PARTS_NUMBER = 2


def check_comma_in_middle(maybe_float: str) -> bool | None:
    parts_number = len(maybe_float.split(","))
    if "," in maybe_float and parts_number == NUM_PARTS_NUMBER:
        return True
    parts_number = len(maybe_float.split("."))
    if "." in maybe_float and parts_number == NUM_PARTS_NUMBER:
        return True
    return None


def check_empty_or_invalid(maybe_float: str) -> bool | None:
    if len(maybe_float) == 0:
        return None
    for char in maybe_float:
        if char not in "0123456789,." or maybe_float == " ":
            return None
    for char in maybe_float:
        if char in ".," and maybe_float.count(char) > 1:
            return None
    num_of_commas = maybe_float.count(",") + maybe_float.count(".")
    if num_of_commas > 1:
        return None
    return True


def sum_into_float(maybe_float: str) -> float | None:
    if check_empty_or_invalid(maybe_float) is None:
        return None
    num_of_commas = maybe_float.count(",") + maybe_float.count(".")
    if (
        ("." in maybe_float and check_comma_in_middle(maybe_float)) or num_of_commas == 0
    ) and not check_comma_in_front_or_back(maybe_float):
        return float(maybe_float)
    num_parts = maybe_float.split(",")
    before_comma = num_parts[0]
    after_comma = num_parts[1]
    if not check_comma_in_middle(maybe_float):
        return None
    return float(f"{before_comma}.{after_comma}")


def format_category_stats(category_stats: CategoryStats) -> str:
    lines = []

    for index, category_stat in enumerate(category_stats, start=1):
        category, amount = category_stat
        lines.append(f"{index}. {category}: {amount:.2f}")

    return "\n".join(lines)


def expense_or_income(amount: float) -> str:
    return "profit" if amount >= 0 else "loss"


def details_handler(date: str) -> str:
    capital, expenses, income, category_stats = stats_handler(date)
    lines = [
        f"Your statistics as of {date}:",
        f"Total capital: {capital:.2f} rubles",
        f"This month, the {expense_or_income(income - expenses)} amounted to {abs(income - expenses):.2f} rubles.",
        f"Income: {income:.2f} rubles",
        f"Expenses: {expenses:.2f} rubles",
        "",
        "Details (category: amount):",
    ]

    if category_stats:
        lines.append(format_category_stats(category_stats))

    return "\n".join(lines)


LENGTH_OF_INCOME_COMMAND = 3
LENGTH_OF_COST_COMMAND = 4
LENGTH_OF_STATS_COMMAND = 2
LENGTH_OF_UNKNOWN_COMMAND_LEFT_BOUNDARE = 4
LENGTH_OF_UNKNOWN_COMMAND_RIGHT_BOUNDARE = 1


def income(parts: list[str]) -> str:
    if len(parts) != LENGTH_OF_INCOME_COMMAND or parts[0] != "income":
        return UNKNOWN_COMMAND_MSG

    amount = sum_into_float(parts[1])
    if amount is None:
        return UNKNOWN_COMMAND_MSG

    return income_handler(amount, parts[2])


LENGTH_OF_COST_CATEGORIES_COMMAND = 2


def cost(parts: list[str]) -> str:
    if len(parts) == LENGTH_OF_COST_CATEGORIES_COMMAND:
        if parts[0] == "cost" and parts[1] == "categories":
            return cost_categories_handler()
        return UNKNOWN_COMMAND_MSG

    if len(parts) != LENGTH_OF_COST_COMMAND or parts[0] != "cost":
        return UNKNOWN_COMMAND_MSG

    amount = sum_into_float(parts[2])
    if amount is None:
        return UNKNOWN_COMMAND_MSG

    return cost_handler(parts[1], amount, parts[3])


def stats(parts: list[str]) -> str:
    if len(parts) != LENGTH_OF_STATS_COMMAND or parts[0] != "stats":
        return UNKNOWN_COMMAND_MSG

    if extract_date(parts[1]) is None:
        return INCORRECT_DATE_MSG

    return details_handler(parts[1])


def process_command(parts: list[str]) -> str:
    if not parts:
        return UNKNOWN_COMMAND_MSG

    command_name = parts[0]

    if command_name == "cost":
        return cost(parts)
    if command_name == "income":
        return income(parts)
    if command_name == "stats":
        return stats(parts)

    return UNKNOWN_COMMAND_MSG


def main() -> None:
    command = input()
    while command != "exit":
        parts = command.split()
        print(process_command(parts))
        command = input()


if __name__ == "__main__":
    main()
