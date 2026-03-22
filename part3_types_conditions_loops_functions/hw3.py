#!/usr/bin/env python
import sys

# Message constants
UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"

# System constants
DATE_PARTS_COUNT = 3
INCOME_CMD_LEN = 3
COST_CMD_LEN = 4
STATS_CMD_LEN = 2
FIRST_MONTH = 1
LAST_MONTH = 12
MIN_DAY = 1
L_MONTH_DAYS = 31
S_MONTH_DAYS = 30
L_FEB_DAYS = 29
C_FEB_DAYS = 28
FEB_NUM = 2
LONG_MONTHS = (1, 3, 5, 7, 8, 10, 12)
SHORT_MONTHS = (4, 6, 9, 11)

# --- REQUIRED FOR TESTS ---
financial_transactions_storage = []
EXPENSE_CATEGORIES = ["Еда", "Транспорт", "Развлечения", "Жилье", "Здоровье"]
NOT_EXISTS_CATEGORY = "NonExistent"


def cost_categories_handler():
    """Returns expense categories."""
    return EXPENSE_CATEGORIES


def is_leap_year(year: int) -> bool:
    """Checks if a year is leap."""
    div_four = year % 4 == 0
    div_hundred = year % 100 == 0
    div_four_hundred = year % 400 == 0
    return (div_four and not div_hundred) or div_four_hundred


def parse_date_parts(maybe_dt: str):
    """Splits date string into integers."""
    parts = maybe_dt.split("-")
    if len(parts) != DATE_PARTS_COUNT:
        return None
    try:
        return [int(p) for p in parts if p.isdigit()]
    except ValueError:
        return None


def days_in_month(month: int, year: int) -> int:
    """Returns number of days in a month."""
    if month in LONG_MONTHS:
        return L_MONTH_DAYS
    if month in SHORT_MONTHS:
        return S_MONTH_DAYS
    if month == FEB_NUM:
        return L_FEB_DAYS if is_leap_year(year) else C_FEB_DAYS
    return 0


def extract_date(maybe_dt: str):
    """Validates and returns date tuple."""
    parsed = parse_date_parts(maybe_dt)
    if not parsed or len(parsed) != DATE_PARTS_COUNT:
        return None
    day, month, year = parsed
    max_d = days_in_month(month, year)
    if month < FIRST_MONTH or month > LAST_MONTH or day < MIN_DAY:
        return None
    if max_d == 0 or day > max_d:
        return None
    return (day, month, year)


def parse_amount(raw: str):
    """Parses string to float safely."""
    try:
        return float(raw.strip().replace(",", "."))
    except ValueError:
        return None


def is_not_later(d1, d2) -> bool:
    """Compares two dates."""
    date_one = (d1[2], d1[1], d1[0])
    date_two = (d2[2], d2[1], d2[0])
    return date_one <= date_two


def is_same_month(d1, d2) -> bool:
    """Checks if month and year match."""
    same_m = d1[1] == d2[1]
    same_y = d1[2] == d2[2]
    return same_m and same_y


def handle_income(incomes, amt_str, dt_str):
    """Handles income."""
    amt = parse_amount(amt_str)
    if amt is None:
        return UNKNOWN_COMMAND_MSG
    if amt <= 0:
        return NONPOSITIVE_VALUE_MSG
    if not extract_date(dt_str):
        return INCORRECT_DATE_MSG
    incomes.append((amt, dt_str))
    financial_transactions_storage.append({"type": "income", "amount": amt, "date": dt_str})
    return f"{OP_SUCCESS_MSG} amount={amt} income_date='{dt_str}'"


def handle_cost(costs, cat, amt_str, dt_str):
    """Handles cost."""
    amt = parse_amount(amt_str)
    dt = extract_date(dt_str)
    if not cat.strip() or amt is None:
        return UNKNOWN_COMMAND_MSG
    if amt <= 0:
        return NONPOSITIVE_VALUE_MSG
    if not dt:
        return INCORRECT_DATE_MSG
    costs.append((cat, amt, dt))
    financial_transactions_storage.append({"type": "cost", "category": cat, "amount": amt, "date": dt_str})
    return f"{OP_SUCCESS_MSG} category_name='{cat}' amount={amt} cost_date='{dt_str}'"


def get_month_stats(incomes, costs, s_dt):
    """Calculates monthly totals."""
    m_inc = 0
    for a, ds in incomes:
        d = extract_date(ds)
        if d and is_same_month(d, s_dt) and is_not_later(d, s_dt):
            m_inc += a
    m_cost, cats = 0, {}
    for c, a, d in costs:
        if is_same_month(d, s_dt) and is_not_later(d, s_dt):
            m_cost += a
            cats[c] = cats.get(c, 0) + a
    return m_inc, m_cost, cats


def format_val(amt):
    """Helper to format float values."""
    if amt.is_integer():
        return str(int(amt))
    return f"{amt:.10f}".rstrip("0").rstrip(".")


def build_lines(date_str, caps):
    """Creates output lines to reduce complexity."""
    t_cap, m_inc, m_cost, m_res, res_msg = caps
    return [
        f"Ваша статистика по состоянию на {date_str}:",
        f"Суммарный капитал: {t_cap:.2f} рублей",
        f"В этом месяце {res_msg} {m_res:.2f} рублей",  # noqa: RUF001
        f"Доходы: {m_inc:.2f} рублей",
        f"Расходы: {m_cost:.2f} рублей",
        "", "Детализация (категория: сумма):"
    ]


def show_stats(incomes, costs, date_str):
    """Shows statistics."""
    s_dt = extract_date(date_str)
    if not s_dt:
        return INCORRECT_DATE_MSG
    t_inc = sum(a for a, ds in incomes if (d := extract_date(ds)) and is_not_later(d, s_dt))
    t_cost = sum(a for _, a, d in costs if is_not_later(d, s_dt))
    m_inc, m_cost, cats = get_month_stats(incomes, costs, s_dt)
    res_msg = "прибыль составила" if m_inc >= m_cost else "убыток составил"
    m_res = abs(m_inc - m_cost)
    lines = build_lines(date_str, (t_inc - t_cost, m_inc, m_cost, m_res, res_msg))
    for i, name in enumerate(sorted(cats), 1):
        lines.append(f"{i}. {name}: {format_val(cats[name])}")
    return "\n".join(lines)


def main():
    """Main function."""
    inc, cos = [], []
    for line in sys.stdin:
        raw = line.strip()
        if not raw:
            break
        p = raw.split()
        if p[0] == "income" and len(p) == INCOME_CMD_LEN:
            print(handle_income(inc, p[1], p[2]))
        elif p[0] == "cost" and len(p) == COST_CMD_LEN:
            print(handle_cost(cos, p[1], p[2], p[3]))
        elif p[0] == "stats" and len(p) == STATS_CMD_LEN:
            print(show_stats(inc, cos, p[1]))
        else:
            print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()
