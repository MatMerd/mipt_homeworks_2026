#!/usr/bin/env python

import re
from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

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

financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    elems = maybe_dt.split('-')
    if len(elems) != 3:
        return None

    day, month, year = elems[0], elems[1], elems[2]

    if not (day.isdigit() and month.isdigit() and year.isdigit()):
        return None

    day, month, year = int(day), int(month), int(year)

    if month < 1 or month > 12:
        return None

    days_in_month = [31, 29 if is_leap_year(year) else 28, 31, 30, 31, 30,
                     31, 31, 30, 31, 30, 31]

    if day < 1 or day > days_in_month[month - 1]:
        return None

    return (day, month, year)


def income_handler(amount: float, income_date: str) -> str:
    financial_transactions_storage.append({"amount": amount, "date": income_date})
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    financial_transactions_storage.append({"category": category_name, "amount": amount, "date": income_date})
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return "\n".join({})


def stats_handler(report_date: str) -> str:
    return f"Statistic for {report_date}"


def main() -> None:
    incomes = []
    expenses = []

    line = input()
    while line:
        elems = line.split()
        command = elems[0]

        match command:
            case "income":
                if len(elems) != 3:
                    print(UNKNOWN_COMMAND_MSG)
                    line = input()
                    continue

                amount_str = elems[1].replace(',', '.')
                if not re.match(r'^\d+([.,]\d+)?$', amount_str):
                    print(NONPOSITIVE_VALUE_MSG)
                    line = input()
                    continue

                amount = float(amount_str)
                if amount <= 0:
                    print(NONPOSITIVE_VALUE_MSG)
                    line = input()
                    continue

                date = extract_date(elems[2])
                if date is None:
                    print(INCORRECT_DATE_MSG)
                    line = input()
                    continue

                incomes.append((date, amount))
                print(OP_SUCCESS_MSG)

            case "cost":
                if len(elems) != 4:
                    print(UNKNOWN_COMMAND_MSG)
                    line = input()
                    continue

                category = elems[1]
                amount_str = elems[2]
                date_str = elems[3]

                if not re.match(r'^\d+([.,]\d+)?$', amount_str):
                    print(NONPOSITIVE_VALUE_MSG)
                    line = input()
                    continue

                amount = float(amount_str)
                if amount <= 0:
                    print(NONPOSITIVE_VALUE_MSG)
                    line = input()
                    continue

                date = extract_date(date_str)
                if date is None:
                    print(INCORRECT_DATE_MSG)
                    line = input()
                    continue

                expenses.append((date, category, amount))
                print(OP_SUCCESS_MSG)

            case "stats":
                if len(elems) != 2:
                    print(UNKNOWN_COMMAND_MSG)
                    line = input()
                    continue

                date = extract_date(elems[1])
                if date is None:
                    print(INCORRECT_DATE_MSG)
                    line = input()
                    continue

                day, month, year = date
                date_str = elems[1]

                total_capital = 0.0
                m_income = 0.0
                m_expenses = 0.0
                categories = {}

                for inc_date, amount in incomes:
                    inc_day, inc_month, inc_year = inc_date

                    if (inc_year < year or
                            (inc_year == year and inc_month < month) or
                            (inc_year == year and inc_month == month and inc_day <= day)):
                        total_capital += amount

                    if inc_month == month and inc_year == year and inc_day <= day:
                        m_income += amount

                for exp_date, category, amount in expenses:
                    exp_day, exp_month, exp_year = exp_date

                    if (exp_year < year or
                            (exp_year == year and exp_month < month) or
                            (exp_year == year and exp_month == month and exp_day <= day)):
                        total_capital -= amount

                    if exp_month == month and exp_year == year and exp_day <= day:
                        m_expenses += amount
                        if category in categories:
                            categories[category] += amount
                        else:
                            categories[category] = amount

                print(f"Ваша статистика по состоянию на {date_str}:")
                print(f"Суммарный капитал: {total_capital:.2f} рублей")

                diff = m_income - m_expenses
                if diff >= 0:
                    print(f"В этом месяце прибыль составила {diff:.2f} рублей")
                else:
                    print(f"В этом месяце убыток составил {abs(diff):.2f} рублей")

                print(f"Доходы: {m_income:.2f} рублей")
                print(f"Расходы: {m_expenses:.2f} рублей")
                print()
                print("Детализация (категория: сумма):")

                if categories:
                    sorted_cats = sorted(categories.keys())
                    counter = 1
                    for cat in sorted_cats:
                        print(f"{counter}. {cat}: {categories[cat]:.2f}")
                        counter += 1
                else:
                    print()

            case _:
                print(UNKNOWN_COMMAND_MSG)

        line = input()


if __name__ == "__main__":
    main()
    
