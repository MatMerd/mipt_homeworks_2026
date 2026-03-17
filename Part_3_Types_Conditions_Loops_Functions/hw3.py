UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"

k1 = 1
k2 = 2
k3 = 3
k4 = 4
k10 = 10
k12 = 12
k29 = 29
k100 = 100
k400 = 400

TOTAL_INDEX = 0
MONTH_INDEX = 1
CATEGORY_INDEX = 2

ParsedDate = tuple[int, int, int]
IncomeRecord = tuple[float, int, int, int]
CostRecord = tuple[str, float, int, int, int]
Incomes = list[IncomeRecord]
Costs = list[CostRecord]
CategorySums = dict[str, float]
CommandParts = list[str]
DAYS_IN_MONTH_TEMPLATE = (
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


def is_divisible(value: int, divider: int) -> bool:
    return value % divider == 0


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    divisible_by_four = is_divisible(year, k4)
    not_divisible_by_hundred = not is_divisible(year, k100)
    divisible_by_four_hundred = is_divisible(year, k400)
    return (divisible_by_four and not_divisible_by_hundred) or divisible_by_four_hundred


def split_date_parts(maybe_dt: str) -> tuple[str, str, str] | None:
    parts = maybe_dt.split("-")
    if len(parts) != k3:
        return None
    return parts[0], parts[k1], parts[k2]


def has_valid_date_lengths(parts: tuple[str, str, str]) -> bool:
    day_length = len(parts[0]) == k2
    month_length = len(parts[k1]) == k2
    year_length = len(parts[k2]) == k4
    return day_length and month_length and year_length


def has_only_digits(parts: tuple[str, str, str]) -> bool:
    return all(part.isdigit() for part in parts)


def build_date(parts: tuple[str, str, str]) -> ParsedDate:
    day = int(parts[0])
    month = int(parts[k1])
    year = int(parts[k2])
    return day, month, year


def get_days_in_month(year: int) -> list[int]:
    days_in_month = list(DAYS_IN_MONTH_TEMPLATE)
    if is_leap_year(year):
        days_in_month[k1] = k29
    return days_in_month


def is_valid_date(date_value: ParsedDate) -> bool:
    day, month, year = date_value
    if month < k1 or month > k12:
        return False
    days_in_month = get_days_in_month(year)
    return k1 <= day <= days_in_month[month - k1]


def extract_date(maybe_dt: str) -> ParsedDate | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: tuple формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    parsed_date = None
    parts = split_date_parts(maybe_dt)
    if parts is not None and has_valid_date_lengths(parts) and has_only_digits(parts):
        candidate_date = build_date(parts)
        if is_valid_date(candidate_date):
            parsed_date = candidate_date
    return parsed_date


def has_valid_amount_separators(amount_string: str) -> bool:
    dots_count = amount_string.count(".")
    commas_count = amount_string.count(",")
    separators_count = dots_count + commas_count
    has_mixed_separators = dots_count > 0 and commas_count > 0
    return separators_count <= k1 and not has_mixed_separators


def normalize_amount_string(amount_string: str) -> str:
    normalized_string = amount_string.replace(",", ".")
    return normalized_string.removeprefix("+")


def is_valid_amount_text(amount_text: str) -> bool:
    if amount_text == "" or amount_text.endswith("."):
        return False
    digits_text = amount_text.replace(".", "")
    return digits_text.isdigit()


def extract_amount(amount_string: str) -> float | None:
    if amount_string == "":
        return None
    if not has_valid_amount_separators(amount_string):
        return None
    normalized_string = normalize_amount_string(amount_string)
    unsigned_string = normalized_string.removeprefix("-")
    if not is_valid_amount_text(unsigned_string):
        return None
    return float(normalized_string)


def is_valid_category(category_name: str) -> bool:
    for symbol in category_name:
        if symbol in {" ", ".", ","}:
            return False
    return category_name != ""


def format_detail_amount(value: float) -> str:
    result = f"{value:.10f}".rstrip("0").rstrip(".")
    return result or "0"


def make_income_record(amount: float, date_value: ParsedDate) -> IncomeRecord:
    return amount, date_value[0], date_value[k1], date_value[k2]


def make_cost_record(category_name: str, amount: float, date_value: ParsedDate) -> CostRecord:
    return category_name, amount, date_value[0], date_value[k1], date_value[k2]


def get_income_amount(income_record: IncomeRecord) -> float:
    amount, _, _, _ = income_record
    return amount


def get_income_date(income_record: IncomeRecord) -> ParsedDate:
    _, day, month, year = income_record
    return day, month, year


def get_cost_category(cost_record: CostRecord) -> str:
    return cost_record[0]


def get_cost_amount(cost_record: CostRecord) -> float:
    return cost_record[1]


def get_cost_date(cost_record: CostRecord) -> ParsedDate:
    day = cost_record[2]
    month = cost_record[3]
    year = cost_record[4]
    return day, month, year


def to_sortable_date(date_value: ParsedDate) -> tuple[int, int, int]:
    return date_value[k2], date_value[k1], date_value[0]


def is_date_on_or_before(date_value: ParsedDate, target_date: ParsedDate) -> bool:
    return to_sortable_date(date_value) <= to_sortable_date(target_date)


def is_same_month(date_value: ParsedDate, target_date: ParsedDate) -> bool:
    same_month = date_value[k1] == target_date[k1]
    same_year = date_value[k2] == target_date[k2]
    return same_month and same_year


def calculate_income_totals(incomes: Incomes, stats_date: ParsedDate) -> tuple[float, float]:
    totals = [float(0), float(0)]
    for income_record in incomes:
        income_date = get_income_date(income_record)
        if is_date_on_or_before(income_date, stats_date):
            income_amount = get_income_amount(income_record)
            totals[TOTAL_INDEX] += income_amount
            if is_same_month(income_date, stats_date):
                totals[MONTH_INDEX] += income_amount
    return totals[TOTAL_INDEX], totals[MONTH_INDEX]


def add_category_sum(category_sums: CategorySums, category_name: str, amount: float) -> None:
    current_sum = category_sums.get(category_name, float(0))
    category_sums[category_name] = current_sum + amount


def calculate_cost_totals(costs: Costs, stats_date: ParsedDate) -> tuple[float, float, CategorySums]:
    totals = [float(0), float(0)]
    category_sums: CategorySums = {}
    for cost_record in costs:
        cost_date = get_cost_date(cost_record)
        if is_date_on_or_before(cost_date, stats_date):
            cost_amount = get_cost_amount(cost_record)
            totals[TOTAL_INDEX] += cost_amount
            if is_same_month(cost_date, stats_date):
                totals[MONTH_INDEX] += cost_amount
                add_category_sum(category_sums, get_cost_category(cost_record), cost_amount)
    return totals[TOTAL_INDEX], totals[MONTH_INDEX], category_sums


def format_stats_date(stats_date: ParsedDate) -> str:
    day = stats_date[0]
    month = stats_date[k1]
    year = stats_date[k2]
    return f"{day:02d}-{month:02d}-{year:04d}"


def print_month_result(month_income: float, month_cost: float) -> None:
    month_delta = month_income - month_cost
    result_text = "прибыль составила"
    result_value = month_delta
    if month_delta < 0:
        result_text = "убыток составил"
        result_value = -month_delta
    print(f"B этом месяце {result_text} {result_value:.2f} рублей")


def print_category_line(index: int, category_name: str, amount: float) -> None:
    formatted_amount = format_detail_amount(amount)
    print(f"{index}. {category_name}: {formatted_amount}")


def print_category_details(category_sums: CategorySums) -> None:
    print()
    print("Детализация (категория: сумма):")
    sorted_categories = sorted(category_sums)
    for index, category_name in enumerate(sorted_categories, start=k1):
        print_category_line(index, category_name, category_sums[category_name])


def print_stats(stats_date: ParsedDate, incomes: Incomes, costs: Costs) -> None:
    income_totals = calculate_income_totals(incomes, stats_date)
    total_cost, month_cost, category_sums = calculate_cost_totals(costs, stats_date)
    total_capital = income_totals[TOTAL_INDEX] - total_cost
    print(f"Ваша статистика по состоянию на {format_stats_date(stats_date)}:")
    print(f"Суммарный капитал: {total_capital:.2f} рублей")
    print_month_result(income_totals[MONTH_INDEX], month_cost)
    print(f"Доходы: {income_totals[MONTH_INDEX]:.2f} рублей")
    print(f"Расходы: {month_cost:.2f} рублей")
    print_category_details(category_sums)


def process_income(parts: CommandParts, incomes: Incomes) -> None:
    if len(parts) != k3:
        print(UNKNOWN_COMMAND_MSG)
        return
    amount = extract_amount(parts[k1])
    if amount is None or amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return
    current_date = extract_date(parts[k2])
    if current_date is None:
        print(INCORRECT_DATE_MSG)
        return
    incomes.append(make_income_record(amount, current_date))
    print(OP_SUCCESS_MSG)


def process_cost(parts: CommandParts, costs: Costs) -> None:
    if len(parts) != k4:
        print(UNKNOWN_COMMAND_MSG)
        return
    category_name = parts[k1]
    if not is_valid_category(category_name):
        print(UNKNOWN_COMMAND_MSG)
        return
    amount = extract_amount(parts[k2])
    if amount is None or amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return
    current_date = extract_date(parts[k3])
    if current_date is None:
        print(INCORRECT_DATE_MSG)
        return
    costs.append(make_cost_record(category_name, amount, current_date))
    print(OP_SUCCESS_MSG)


def process_stats(parts: CommandParts, incomes: Incomes, costs: Costs) -> None:
    if len(parts) != k2:
        print(UNKNOWN_COMMAND_MSG)
        return
    current_date = extract_date(parts[k1])
    if current_date is None:
        print(INCORRECT_DATE_MSG)
        return
    print_stats(current_date, incomes, costs)


def process_command(parts: CommandParts, incomes: Incomes, costs: Costs) -> None:
    command = parts[0]
    if command == "income":
        process_income(parts, incomes)
    elif command == "cost":
        process_cost(parts, costs)
    elif command == "stats":
        process_stats(parts, incomes, costs)
    else:
        print(UNKNOWN_COMMAND_MSG)


def process_line(raw_line: str, incomes: Incomes, costs: Costs) -> None:
    line = raw_line.strip()
    if line == "":
        print(UNKNOWN_COMMAND_MSG)
        return
    process_command(line.split(), incomes, costs)


def run_process() -> None:
    incomes: Incomes = []
    costs: Costs = []
    with open(0) as input_stream:
        for raw_line in input_stream:
            process_line(raw_line, incomes, costs)


def main() -> None:
    """Ваш код здесь."""
    run_process()


if __name__ == "__main__":
    main()
