#!/usr/bin/env python

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
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0


def get_days_in_month(month: int, year: int) -> int:
    """Возвращает количество дней в месяце"""
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    if month == 2 and is_leap_year(year):
        return 29
    return days_in_month[month - 1]


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    parts = maybe_dt.split("-")

    if len(parts) != 3:
        return None

    try:
        day = int(parts[0])
        month = int(parts[1])
        year = int(parts[2])
    except ValueError:
        return None

    if month < 1 or month > 12:
        return None

    if day < 1 or day > get_days_in_month(month, year):
        return None

    return (day, month, year)


def validate_amount(amount_str: str) -> float | None:
    """Проверяет и преобразует сумму"""
    amount_str = amount_str.replace(",", ".")
    for char in amount_str:
        if char not in "0123456789.-":
            return None

    if amount_str.count(".") > 1:
        return None

    try:
        return float(amount_str)
    except ValueError:
        return None


def validate_category(category_name: str) -> bool:
    """Проверяет существование категории в формате common::target"""
    if "::" not in category_name:
        return False

    common, target = category_name.split("::", 1)

    return bool(common in EXPENSE_CATEGORIES and target in EXPENSE_CATEGORIES[common])


def get_all_categories() -> list[str]:
    """Возвращает список всех категорий в формате common::target"""
    categories = []
    for common, targets in EXPENSE_CATEGORIES.items():
        for target in targets:
            categories.append(f"{common}::{target}")
    return sorted(categories)


def calculate_total_capital(day: int, month: int, year: int) -> float:
    """Расчет суммарного капитала до указанной даты"""
    total = 0.0

    for transaction in financial_transactions_storage:
        trans_date = extract_date(transaction["date"])
        if trans_date is None:
            continue

        trans_day, trans_month, trans_year = trans_date

        if (
            trans_year < year
            or (trans_year == year and trans_month < month)
            or (trans_year == year and trans_month == month and trans_day <= day)
        ):
            if transaction["type"] == "income":
                total += transaction["amount"]
            else:
                total -= transaction["amount"]

    return total


def get_monthly_stats(day: int, month: int, year: int) -> tuple[float, float, dict[str, float]]:
    """Получение статистики за текущий месяц до указанного дня"""
    monthly_income = 0.0
    monthly_expenses = 0.0
    expenses_by_category = {}

    for transaction in financial_transactions_storage:
        trans_date = extract_date(transaction["date"])
        if trans_date is None:
            continue

        trans_day, trans_month, trans_year = trans_date

        if trans_year == year and trans_month == month and trans_day <= day:
            if transaction["type"] == "income":
                monthly_income += transaction["amount"]
            else:
                monthly_expenses += transaction["amount"]
                category = transaction.get("category", "")
                target_category = category.split("::")[1] if "::" in category else category

                expenses_by_category[target_category] = (
                    expenses_by_category.get(target_category, 0) + transaction["amount"]
                )

    return monthly_income, monthly_expenses, expenses_by_category


def income_handler(amount: float, income_date: str) -> str:
    financial_transactions_storage.append({"type": "income", "amount": amount, "date": income_date})
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    financial_transactions_storage.append(
        {"type": "expense", "category": category_name, "amount": amount, "date": income_date}
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    categories = get_all_categories()
    return "\n".join(categories)


def stats_handler(report_date: str) -> str:
    """Обработчик статистики"""
    date_tuple = extract_date(report_date)
    if date_tuple is None:
        return INCORRECT_DATE_MSG

    day, month, year = date_tuple

    total_capital = calculate_total_capital(day, month, year)
    monthly_income, monthly_expenses, expenses_by_category = get_monthly_stats(day, month, year)

    profit_loss = monthly_income - monthly_expenses

    result = []
    result.append(f"Your statistics as of {report_date}:")
    result.append(f"Total capital: {total_capital:.2f} rubles")

    if profit_loss >= 0:
        result.append(f"This month, the profit amounted to {profit_loss:.2f} rubles.")
    else:
        result.append(f"This month, the loss amounted to {abs(profit_loss):.2f} rubles.")

    result.append(f"Income: {monthly_income:.2f} rubles")
    result.append(f"Expenses: {monthly_expenses:.2f} rubles")

    if expenses_by_category:
        result.append("Details (category: amount):")
        sorted_categories = sorted(expenses_by_category.items())
        for i, (category, amount) in enumerate(sorted_categories, 1):
            result.append(f"{i}. {category}: {amount:.0f}")
    else:
        result.append("Details (category: amount):")

    return "\n".join(result)


def main() -> None:
    """Главная функция для обработки команд"""
    while True:
        try:
            command_line = input().strip()

            if not command_line:
                continue

            parts = command_line.split()
            command = parts[0].lower()

            if command == "exit":
                break

            if command == "income" and len(parts) == 3:
                amount_str = parts[1]
                date_str = parts[2]

                if extract_date(date_str) is None:
                    print(INCORRECT_DATE_MSG)
                    continue

                amount = validate_amount(amount_str)
                if amount is None:
                    print(UNKNOWN_COMMAND_MSG)
                    continue

                if amount <= 0:
                    print(NONPOSITIVE_VALUE_MSG)
                    continue

                print(income_handler(amount, date_str))

            elif command == "cost":
                if len(parts) == 2 and parts[1] == "categories":
                    print(cost_categories_handler())
                elif len(parts) == 4:
                    category_name = parts[1]
                    amount_str = parts[2]
                    date_str = parts[3]

                    if extract_date(date_str) is None:
                        print(INCORRECT_DATE_MSG)
                        continue

                    amount = validate_amount(amount_str)
                    if amount is None:
                        print(UNKNOWN_COMMAND_MSG)
                        continue

                    if amount <= 0:
                        print(NONPOSITIVE_VALUE_MSG)
                        continue

                    if not validate_category(category_name):
                        print(NOT_EXISTS_CATEGORY)
                        print(cost_categories_handler())
                        continue

                    print(cost_handler(category_name, amount, date_str))
                else:
                    print(UNKNOWN_COMMAND_MSG)

            elif command == "stats" and len(parts) == 2:
                date_str = parts[1]
                print(stats_handler(date_str))

            else:
                print(UNKNOWN_COMMAND_MSG)

        except EOFError:
            break


if __name__ == "__main__":
    main()
