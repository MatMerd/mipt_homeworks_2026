#!/usr/bin/env python
UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "The value must be greater than zero!"
INCORRECT_DATE_MSG = "Incorrect date!"
OP_SUCCESS_MSG = "Added"
STATS_HEADER_PREFIX = "Your statistics as of"
TOTAL_CAPITAL_LABEL = "Total capital"
MONTH_PROFIT_PREFIX = "This month profit is"
MONTH_LOSS_PREFIX = "This month loss is"
INCOME_LABEL = "Income"
COST_LABEL = "Expenses"
RUBLES_LABEL = "rubles"

DAY_PART_LEN = 2
YEAR_PART_LEN = 4
DATE_PARTS_COUNT = 3
INCOME_PARTS_COUNT = 3
COST_PARTS_COUNT = 4
STATS_PARTS_COUNT = 2
MIN_DAY = 1
MIN_MONTH = 1
MAX_MONTH = 12
FEBRUARY = 2
DAYS_IN_SHORT_FEBRUARY = 28
DAYS_IN_LEAP_FEBRUARY = 29
DAYS_IN_MEDIUM_MONTH = 30
DAYS_IN_LONG_MONTH = 31
MEDIUM_MONTHS = (4, 6, 9, 11)

Operation = tuple[float, int, int, int]
IncomeHistory = list[Operation]
CostHistory = dict[str, list[Operation]]
DateTuple = tuple[int, int, int]
StatsDetails = dict[str, float]
StatsResult = tuple[float, float, float, StatsDetails]


def output(message: str = "") -> None:
    print(message)  # noqa: T201


def is_leap_year(year: int) -> bool:
    """
    Determine whether a year is leap (True) or non-leap (False).

    :param int year: Year to validate
    :return: Leap-year flag.
    :rtype: bool
    """
    if year % 4 == 0 and year % 100 != 0:
        return True

    if year % 100 == 0:
        return year % 400 == 0

    return False


def is_decimal_part(value: str) -> bool:
    return value == "" or value.isdigit()


def is_valid_number(maybe_num: str) -> bool:
    normalized = maybe_num.replace(",", ".")
    if normalized.count(".") > 1:
        return False

    unsigned = normalized.removeprefix("-")
    if unsigned == "":
        return False

    if "." not in unsigned:
        return unsigned.isdigit()

    left, right = unsigned.split(".", 1)
    has_digits = left != "" or right != ""
    return has_digits and is_decimal_part(left) and is_decimal_part(right)


def is_valid_category(category: str) -> bool:
    return category != "" and "." not in category and "," not in category


def is_valid_date_text_parts(day: str, month: str, year: str) -> bool:
    if not (day.isdigit() and month.isdigit() and year.isdigit()):
        return False

    return (len(day), len(month), len(year)) == (
        DAY_PART_LEN,
        DAY_PART_LEN,
        YEAR_PART_LEN,
    )


def days_in_month(month: int, year: int) -> int:
    if month == FEBRUARY:
        if is_leap_year(year):
            return DAYS_IN_LEAP_FEBRUARY
        return DAYS_IN_SHORT_FEBRUARY

    if month in MEDIUM_MONTHS:
        return DAYS_IN_MEDIUM_MONTH

    return DAYS_IN_LONG_MONTH


def parse_date_parts(parts: list[str]) -> DateTuple | None:
    day_value = int(parts[0])
    month_value = int(parts[1])
    year_value = int(parts[2])

    if month_value < MIN_MONTH or month_value > MAX_MONTH:
        return None

    month_days = days_in_month(month_value, year_value)
    if day_value < MIN_DAY or day_value > month_days:
        return None

    return day_value, month_value, year_value


def extract_date(maybe_dt: str) -> DateTuple | None:
    date_parts = maybe_dt.split("-")
    if len(date_parts) != DATE_PARTS_COUNT:
        return None

    if not is_valid_date_text_parts(date_parts[0], date_parts[1], date_parts[2]):
        return None

    return parse_date_parts(date_parts)


def iter_input_lines() -> list[str]:
    with open(0) as stdin:
        return stdin.readlines()


def is_in_target_month(operation: Operation, target: DateTuple) -> bool:
    if operation[3] != target[2]:
        return False

    if operation[2] != target[1]:
        return False

    return operation[1] <= target[0]


def is_on_or_before(operation: Operation, target_date: DateTuple) -> bool:
    return (operation[3], operation[2], operation[1]) <= target_date


def income_until_date(incomes: IncomeHistory, target_date: DateTuple) -> float:
    return sum(operation[0] for operation in incomes if is_on_or_before(operation, target_date))


def income_in_month(incomes: IncomeHistory, target: DateTuple) -> float:
    return sum(operation[0] for operation in incomes if is_in_target_month(operation, target))


def calculate_income_totals(
    incomes: IncomeHistory,
    target: DateTuple,
    target_date: DateTuple,
) -> tuple[float, float]:
    return income_until_date(incomes, target_date), income_in_month(incomes, target)


def cost_until_date(operations: list[Operation], target_date: DateTuple) -> float:
    return sum(operation[0] for operation in operations if is_on_or_before(operation, target_date))


def cost_in_month(operations: list[Operation], target: DateTuple) -> float:
    return sum(operation[0] for operation in operations if is_in_target_month(operation, target))


def build_month_details(costs: CostHistory, target: DateTuple) -> StatsDetails:
    details: StatsDetails = {}
    for category, operations in costs.items():
        category_sum = cost_in_month(operations, target)
        if category_sum > float(0):
            details[category] = category_sum
    return details


def total_cost_until_date(costs: CostHistory, target_date: DateTuple) -> float:
    return sum(cost_until_date(operations, target_date) for operations in costs.values())


def calculate_cost_totals(
    costs: CostHistory,
    target: DateTuple,
    target_date: DateTuple,
) -> tuple[float, float, StatsDetails]:
    details = build_month_details(costs, target)
    return total_cost_until_date(costs, target_date), sum(details.values()), details


def make_target_date(target: DateTuple) -> DateTuple:
    return target[2], target[1], target[0]


def calculate_stats(
    target: DateTuple,
    incomes: IncomeHistory,
    costs: CostHistory,
) -> StatsResult:
    current_target_date = make_target_date(target)
    income_totals = calculate_income_totals(incomes, target, current_target_date)
    cost_totals = calculate_cost_totals(costs, target, current_target_date)
    return (
        income_totals[0] - cost_totals[0],
        income_totals[1],
        cost_totals[1],
        cost_totals[2],
    )


def format_detail_value(value: float) -> str:
    if value.is_integer():
        return str(int(value))

    return f"{value:.2f}"


def print_details(details: StatsDetails) -> None:
    output("Breakdown (category: amount):")
    for index, category in enumerate(sorted(details), start=1):
        value_text = format_detail_value(details[category])
        output(f"{index}. {category}: {value_text}")


def show_month_balance(month_income: float, month_cost: float) -> None:
    if month_income >= month_cost:
        profit = month_income - month_cost
        output(f"{MONTH_PROFIT_PREFIX} {profit:.2f} {RUBLES_LABEL}")
        return

    loss = month_cost - month_income
    output(f"{MONTH_LOSS_PREFIX} {loss:.2f} {RUBLES_LABEL}")


def print_stats_report(date_text: str, stats: StatsResult) -> None:
    total_capital, month_income, month_cost, details = stats
    output(f"{STATS_HEADER_PREFIX} {date_text}:")
    output(f"{TOTAL_CAPITAL_LABEL}: {total_capital:.2f} {RUBLES_LABEL}")
    show_month_balance(month_income, month_cost)
    output(f"{INCOME_LABEL}: {month_income:.2f} {RUBLES_LABEL}")
    output(f"{COST_LABEL}: {month_cost:.2f} {RUBLES_LABEL}")
    output()
    print_details(details)


def operation_from_amount_and_date(amount: float, date: DateTuple) -> Operation:
    return amount, date[0], date[1], date[2]


def handle_income(command: list[str], incomes: IncomeHistory) -> None:
    if len(command) != INCOME_PARTS_COUNT:
        output(UNKNOWN_COMMAND_MSG)
        return

    amount_text = command[1].replace(",", ".")
    if not is_valid_number(amount_text):
        output(UNKNOWN_COMMAND_MSG)
        return

    date = extract_date(command[2])
    if date is None:
        output(INCORRECT_DATE_MSG)
        return

    amount = float(amount_text)
    if amount <= float(0):
        output(NONPOSITIVE_VALUE_MSG)
        return

    incomes.append(operation_from_amount_and_date(amount, date))
    output(OP_SUCCESS_MSG)


def add_cost_operation(costs: CostHistory, category: str, operation: Operation) -> None:
    if category not in costs:
        costs[category] = []

    costs[category].append(operation)


def handle_cost(command: list[str], costs: CostHistory) -> None:
    if len(command) != COST_PARTS_COUNT:
        output(UNKNOWN_COMMAND_MSG)
        return

    amount_text = command[2].replace(",", ".")
    if not is_valid_number(amount_text):
        output(UNKNOWN_COMMAND_MSG)
        return

    date = extract_date(command[3])
    if date is None:
        output(INCORRECT_DATE_MSG)
        return

    category = command[1]
    if not is_valid_category(category):
        output(UNKNOWN_COMMAND_MSG)
        return

    amount = float(amount_text)
    if amount <= float(0):
        output(NONPOSITIVE_VALUE_MSG)
        return

    add_cost_operation(costs, category, operation_from_amount_and_date(amount, date))
    output(OP_SUCCESS_MSG)


def handle_stats(command: list[str], incomes: IncomeHistory, costs: CostHistory) -> None:
    if len(command) != STATS_PARTS_COUNT:
        output(UNKNOWN_COMMAND_MSG)
        return

    date = extract_date(command[1])
    if date is None:
        output(INCORRECT_DATE_MSG)
        return

    stats = calculate_stats(date, incomes, costs)
    print_stats_report(command[1], stats)


def process_line(line: str, incomes: IncomeHistory, costs: CostHistory) -> None:
    command = line.split()
    if not command:
        output(UNKNOWN_COMMAND_MSG)
        return

    command_name = command[0]
    if command_name == "income":
        handle_income(command, incomes)
        return

    if command_name == "cost":
        handle_cost(command, costs)
        return

    if command_name == "stats":
        handle_stats(command, incomes, costs)
        return

    output(UNKNOWN_COMMAND_MSG)


def main() -> None:
    """Entry point."""
    incomes: IncomeHistory = []
    costs: CostHistory = {}

    for line in iter_input_lines():
        process_line(line, incomes, costs)


if __name__ == "__main__":
    main()
