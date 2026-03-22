#!/usr/bin/env python

import re
from typing import Any, Optional

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be greater than zero!"
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
    "Other": ("Other",),
}

financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def extract_date(maybe_dt: str) -> Optional[tuple[int, int, int]]:
    elems = maybe_dt.split("-")
    if len(elems) != 3:
        return None

    day, month, year = elems[0], elems[1], elems[2]

    if not (day.isdigit() and month.isdigit() and year.isdigit()):
        return None

    day, month, year = int(day), int(month), int(year)

    if year < 1 or month < 1 or month > 12 or day < 1:
        return None

    days_in_month = [31, 29 if is_leap_year(year) else 28, 31, 30, 31, 30,
                     31, 31, 30, 31, 30, 31]

    if day > days_in_month[month - 1]:
        return None

    return (day, month, year)


def income_handler(amount: float, income_date: str) -> str:
    date_tuple = extract_date(income_date)
    if date_tuple is None:
        return INCORRECT_DATE_MSG

    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    financial_transactions_storage.append({"amount": amount, "date": date_tuple})
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    date_tuple = extract_date(income_date)
    if date_tuple is None:
        return INCORRECT_DATE_MSG

    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    if "::" not in category_name:
        return NOT_EXISTS_CATEGORY

    common_cat, target_cat = category_name.split("::")
    if common_cat not in EXPENSE_CATEGORIES or target_cat not in EXPENSE_CATEGORIES[common_cat]:
        return NOT_EXISTS_CATEGORY

    financial_transactions_storage.append({"category": category_name, "amount": amount, "date": date_tuple})
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    result = []
    for common_cat, sub_cats in EXPENSE_CATEGORIES.items():
        for sub_cat in sub_cats:
            result.append(f"{common_cat}::{sub_cat}")
    return "\n".join(result)


def stats_handler(report_date: str) -> str:
    date_tuple = extract_date(report_date)
    if date_tuple is None:
        return INCORRECT_DATE_MSG

    target_day, target_month, target_year = date_tuple
    total_capital = 0.0
    month_income = 0.0
    month_expenses = 0.0
    categories = {}

    for transaction in financial_transactions_storage:
        if not transaction or "date" not in transaction:
            continue

        trans_day, trans_month, trans_year = transaction["date"]
        amount = transaction["amount"]

        is_cost = "category" in transaction

        if (trans_year < target_year or
                (trans_year == target_year and trans_month < target_month) or
                (trans_year == target_year and trans_month == target_month and trans_day <= target_day)):

            if is_cost:
                total_capital -= amount
            else:
                total_capital += amount

        if trans_month == target_month and trans_year == target_year and trans_day <= target_day:
            if is_cost:
                month_expenses += amount
                cat_name = transaction["category"]
                categories[cat_name] = categories.get(cat_name, 0.0) + amount
            else:
                month_income += amount

    month_result = month_income - month_expenses

    result = f"Ваша статистика по состоянию на {report_date}:\n"
    result += f"Суммарный капитал: {total_capital:.2f} рублей\n"

    if month_result >= 0:
        result += f"В этом месяце прибыль составила {month_result:.2f} рублей\n"
    else:
        result += f"В этом месяце убыток составил {abs(month_result):.2f} рублей\n"

    result += f"Доходы: {month_income:.2f} рублей\n"
    result += f"Расходы: {month_expenses:.2f} рублей\n"
    result += "Детализация (категория: сумма):\n"

    if categories:
        sorted_cats = sorted(categories.keys())
        for i, cat in enumerate(sorted_cats, 1):
            display_cat = cat.split("::")[1] if "::" in cat else cat
            amount = categories[cat]
            if amount.is_integer():
                result += f"{i}. {display_cat}: {int(amount)}\n"
            else:
                result += f"{i}. {display_cat}: {amount:.2f}\n"
    else:
        result += "\n"

    return result.rstrip()


def main() -> None:
    try:
        line = input().strip()
    except EOFError:
        return

    while line:
        if not line:
            try:
                line = input().strip()
            except EOFError:
                break
            continue

        elems = line.split()
        command = elems[0]

        match command:
            case "income":
                if len(elems) != 3:
                    print(UNKNOWN_COMMAND_MSG)
                else:
                    amount_str = elems[1].replace(",", ".")
                    if not re.match(r"^\d+(\.\d+)?$", amount_str):
                        print(NONPOSITIVE_VALUE_MSG)
                    else:
                        amount = float(amount_str)
                        result = income_handler(amount, elems[2])
                        print(result)

            case "cost":
                if len(elems) == 2 and elems[1] == "categories":
                    print(cost_categories_handler())
                elif len(elems) == 4:
                    category = elems[1]
                    amount_str = elems[2].replace(",", ".")
                    date_str = elems[3]

                    if not re.match(r"^\d+(\.\d+)?$", amount_str):
                        print(NONPOSITIVE_VALUE_MSG)
                    else:
                        amount = float(amount_str)
                        result = cost_handler(category, amount, date_str)
                        print(result)
                else:
                    print(UNKNOWN_COMMAND_MSG)

            case "stats":
                if len(elems) != 2:
                    print(UNKNOWN_COMMAND_MSG)
                else:
                    result = stats_handler(elems[1])
                    print(result)

            case _:
                print(UNKNOWN_COMMAND_MSG)

        try:
            line = input().strip()
        except EOFError:
            break


if __name__ == "__main__":
    main()