
#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

MONTH_PROFIT_PREFIX = "This month, the profit amounted to"
MONTH_LOSS_PREFIX = "This month, the loss amounted to"

FEBRUARY = 2
DATE_PARTS_COUNT = 3
DAY_LEN = 2
MONTH_LEN = 2
YEAR_LEN = 4
INCOME_PARTS_COUNT = 3
COST_PARTS_COUNT = 4
STATS_PARTS_COUNT = 2
MAX_MONTH = 12
CATEGORY_NAME_PARTS = 2

Types = tuple[float, int, int, int]
IncomesState: list[Types] = []
CostsState: dict[str, list[Types]] = {}
DateType = tuple[int, int, int]
StatsType = tuple[float, float, float, dict[str, float]]

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": (),
}

financial_transactions_storage: list[dict[str, object]] = []


def iter_input_lines() -> list[str]:
    with open(0) as stdin:
        return stdin.readlines()


def output(message: str = "") -> None:
    print(message)


def input_request(request: str) -> None:
    command = request.split()
    if not command:
        output(UNKNOWN_COMMAND_MSG)
        return
    command_name = command[0]
    if command_name == "income":
        if check_income(command):
            output(income_handler(float(command[1].replace(",", ".")), command[2]))
    elif command_name == "cost":
        if check_cost(command):
            output(cost_handler(command[1], float(command[2]), command[3]))
    elif command_name == "stats":
        if check_stats(command):
            stats_handler(command[1])
    else:
        output(UNKNOWN_COMMAND_MSG)


def check_income(command: list) -> bool:
    if len(command) != INCOME_PARTS_COUNT:
        output(UNKNOWN_COMMAND_MSG)
        return False
    if not check_amount(command[1]):
        output(UNKNOWN_COMMAND_MSG)
        return False
    if float(command[1].replace(",", ".")) <= 0:
        output(NONPOSITIVE_VALUE_MSG)
        return False
    date = extract_date(command[2])
    if date is None:
        output(INCORRECT_DATE_MSG)
        return False
    return True


def check_cost(command: list) -> bool:
    if len(command) == COST_PARTS_COUNT and command[1] == "categories":
        output(cost_categories_handler())
        return False
    if len(command) != COST_PARTS_COUNT:
        output(UNKNOWN_COMMAND_MSG)
        return False
    if not is_valid_category(command[1]):
        output(NOT_EXISTS_CATEGORY)
        output(cost_categories_handler())
        return False
    if not check_amount(command[2].replace(",", ".")):
        output(UNKNOWN_COMMAND_MSG)
        return False
    return check_amount_cost(command)


def check_amount_cost(command: list) -> bool:
    amount = float(command[2].replace(",", "."))
    if amount <= 0:
        output(NONPOSITIVE_VALUE_MSG)
        return False
    date = extract_date(command[3])
    if date is None:
        output(INCORRECT_DATE_MSG)
        return False
    return True


def check_stats(command: list) -> bool:
    if len(command) != STATS_PARTS_COUNT:
        output(UNKNOWN_COMMAND_MSG)
        return False
    command_date = command[1]
    date = extract_date(command_date)
    if date is None:
        output(INCORRECT_DATE_MSG)
        return False
    return True


def is_valid_category(category: str) -> bool:
    if category == "" or " " in category or "." in category or "," in category:
        return False
    parts = category.split("::")
    if len(parts) != CATEGORY_NAME_PARTS:
        return False
    common_category, target_category = parts
    if common_category not in EXPENSE_CATEGORIES:
        return False
    return target_category in EXPENSE_CATEGORIES[common_category]


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


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    date_parts = maybe_dt.split("-")
    if not is_valid_text_date_parts(date_parts):
        return None
    return parse_date_parts(date_parts)


def is_valid_text_date_parts(parts: list[str]) -> bool:
    if len(parts) != DATE_PARTS_COUNT:
        return False
    day_text, month_text, year_text = parts
    if not (day_text.isdigit() and month_text.isdigit() and year_text.isdigit()):
        return False
    return (
        len(day_text) == DAY_LEN
        and len(month_text) == MONTH_LEN
        and len(year_text) == YEAR_LEN
    )


def parse_date_parts(parts: list[str]) -> tuple[int, int, int] | None:
    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2])
    if month < 1 or month > MAX_MONTH:
        return None
    month_days = days_in_month(month, year)
    if day < 1 or day > month_days:
        return None
    return day, month, year


def days_in_month(month: int, year: int) -> int:
    if month == FEBRUARY:
        if is_leap_year(year):
            return 29
        return 28
    if month in (1, 3, 5, 7, 8, 10, 12):
        return 31
    return 30


def income_handler(amount: float, income_date: str) -> str:
    IncomesState.append(make_operation(amount, extract_date(income_date)))
    financial_transactions_storage.append({"amount": amount, "date": income_date})
    return OP_SUCCESS_MSG


def make_operation(amount: float, date: DateType) -> Types:
    return amount, date[0], date[1], date[2]


def check_amount(amount: str) -> bool:
    amount = amount.replace(",", ".")
    if amount.count(".") > 1:
        return False
    amount = amount.removeprefix("-")
    if amount == "":
        return False
    if "." not in amount:
        return amount.isdigit()
    left, right = amount.split(".", 1)
    return left.isdigit() and right.isdigit()


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if category_name not in CostsState:
        CostsState[category_name] = []
    CostsState[category_name].append(make_operation(amount, extract_date(income_date)))
    financial_transactions_storage.append(
        {"category": category_name, "amount": amount, "date": income_date}
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return "\n".join(
        f"{common_category}::{target_category}"
        for common_category, targets in EXPENSE_CATEGORIES.items()
        for target_category in targets
    )


def stats_handler(report_date: str) -> str:
    total_capital, month_income, month_cost, dict_of_costs = calculate_stats(
        extract_date(report_date)
    )
    print_stats(
        report_date,
        total_capital,
        month_income,
        month_cost,
        dict_of_costs,
    )
    return f"Statistic for {report_date}"


def calculate_stats(date: DateType) -> StatsType:
    all_incomes = incomes_total(date)
    all_costs = costs_total(date)
    incomes_in_this_month = incomes_in_month(date)
    costs_in_this_month = costs_in_month(date)
    dict_of_costs = amount_on_categories(date)
    return (
        all_incomes - all_costs,
        incomes_in_this_month,
        costs_in_this_month,
        dict_of_costs,
    )


def print_stats(
    date: str,
    total_capital: float,
    incomes_in_this_month: float,
    costs_in_this_month: float,
    dict_of_costs: dict[str, float],
) -> None:
    output(f"Your statistics as of {date}:")
    output(f"Total capital: {total_capital:.2f} rubles")
    if incomes_in_this_month >= costs_in_this_month:
        profit = incomes_in_this_month - costs_in_this_month
        output(f"{MONTH_PROFIT_PREFIX} {profit:.2f} rubles.")
    else:
        loss = costs_in_this_month - incomes_in_this_month
        output(f"{MONTH_LOSS_PREFIX} {loss:.2f} rubles.")
    output(f"Income: {incomes_in_this_month:.2f} rubles")
    output(f"Expenses: {costs_in_this_month:.2f} rubles")
    output()
    output("Details (category: amount):")
    for count, category in enumerate(sorted(dict_of_costs), start=1):
        output(f"{count}. {category}: {change_format(dict_of_costs[category])}")


def change_format(amount: float) -> str:
    if amount.is_integer():
        return str(int(amount))
    return f"{amount:.2f}"


def amount_on_categories(date: DateType) -> dict[str, float]:
    dict_of_costs: dict[str, float] = {}
    for category, operations in CostsState.items():
        summa_category: float = 0
        for operation in operations:
            if this_month_or_not(operation[1], operation[2], operation[3], date):
                summa_category += operation[0]
        if summa_category > 0:
            target_category = category.split("::")[1]
            dict_of_costs[target_category] = summa_category
    return dict_of_costs


def incomes_total(date: DateType) -> float:
    total: float = 0
    for operation in IncomesState:
        if before_date_or_not(operation[1], operation[2], operation[3], date):
            total += operation[0]
    return total


def incomes_in_month(date: DateType) -> float:
    total: float = 0
    for operation in IncomesState:
        if this_month_or_not(operation[1], operation[2], operation[3], date):
            total += operation[0]
    return total


def costs_total(date: DateType) -> float:
    total: float = 0
    for operations in CostsState.values():
        for operation in operations:
            if before_date_or_not(operation[1], operation[2], operation[3], date):
                total += operation[0]
    return total


def costs_in_month(date: DateType) -> float:
    total: float = 0
    for operations in CostsState.values():
        for operation in operations:
            if this_month_or_not(operation[1], operation[2], operation[3], date):
                total += operation[0]
    return total


def before_date_or_not(day: int, month: int, year: int, date: DateType) -> bool:
    target = date[2], date[1], date[0]
    operation = year, month, day
    return operation <= target


def this_month_or_not(day: int, month: int, year: int, date: DateType) -> bool:
    same_year = year == date[2]
    same_month = month == date[1]
    same_day_or_before = day <= date[0]
    return same_year and same_month and same_day_or_before


def main() -> None:
    for request in iter_input_lines():
        input_request(request)


if __name__ == "__main__":
    main()
