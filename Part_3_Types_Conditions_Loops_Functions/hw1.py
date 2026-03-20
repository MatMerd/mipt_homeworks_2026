EXPENSE_CATEGORIES = {
    "Housing": ["Rent", "Utilities", "Repairs"],
    "Food": ["Groceries", "FastFood", "Restaurants"],
    "Transport": ["Public", "Taxi", "Fuel"],
    "Entertainment": ["Cinema", "Gaming", "Subscriptions"],
    "Shopping": ["Clothes", "Electronics", "Gifts"],
    "Health": ["Pharmacy", "Doctor", "Sport"],
    "Education": ["Courses", "Books", "Materials"],
    "Other": ["Other"],
}

incomes = []
expenses = []


def is_leap_year(year):
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0


def get_days_in_month(month, year):
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    if month == 2 and is_leap_year(year):
        return 29
    return days_in_month[month - 1]


def validate_date(date_str):
    parts = date_str.split("-")

    if len(parts) != 3:
        return False

    try:
        day = int(parts[0])
        month = int(parts[1])
        year = int(parts[2])
    except ValueError:
        return False

    if month < 1 or month > 12:
        return False

    return not (day < 1 or day > get_days_in_month(month, year))


def parse_date(date_str):
    parts = date_str.split("-")
    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2])
    return day, month, year


def validate_amount(amount_str):
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


def add_income(amount_str, date_str):
    if not validate_date(date_str):
        print("Invalid date!")
        return
    amount = validate_amount(amount_str)
    if amount is None:
        print("Unknown command!")
        return
    if amount <= 0:
        print("Value must be grater than zero!")
        return
    day, month, year = parse_date(date_str)
    incomes.append((amount, day, month, year))
    print("Added")


def get_all_categories():
    categories = []
    for common, targets in EXPENSE_CATEGORIES.items():
        for target in targets:
            categories.append(f"{common}::{target}")
    return categories


def validate_category(category_str):
    if "::" not in category_str:
        return False

    common, target = category_str.split("::", 1)

    return bool(common in EXPENSE_CATEGORIES and target in EXPENSE_CATEGORIES[common])


def print_available_categories():
    print("Available categories:")
    categories = get_all_categories()
    for cat in sorted(categories):
        print(f"  {cat}")


def add_expense(category_name, amount_str, date_str):
    if not validate_date(date_str):
        print("Invalid date!")
        return

    amount = validate_amount(amount_str)
    if amount is None:
        print("Unknown command!")
        return

    if amount <= 0:
        print("Value must be grater than zero!")
        return

    if not validate_category(category_name):
        print("Category not exists!")
        print_available_categories()
        return

    day, month, year = parse_date(date_str)
    expenses.append((amount, category_name, day, month, year))
    print("Added")


def calculate_total_capital(up_to_day, up_to_month, up_to_year):
    total = 0

    for income in incomes:
        amount, day, month, year = income
        if (
            year < up_to_year
            or (year == up_to_year and month < up_to_month)
            or (year == up_to_year and month == up_to_month and day <= up_to_day)
        ):
            total += amount

    for expense in expenses:
        amount, _, day, month, year = expense
        if (
            year < up_to_year
            or (year == up_to_year and month < up_to_month)
            or (year == up_to_year and month == up_to_month and day <= up_to_day)
        ):
            total -= amount

    return total


def get_monthly_stats(day, month, year):
    monthly_income = 0
    monthly_expenses = 0
    expenses_by_category = {}

    for income in incomes:
        amount, inc_day, inc_month, inc_year = income
        if inc_year == year and inc_month == month and inc_day <= day:
            monthly_income += amount

    for expense in expenses:
        amount, category, exp_day, exp_month, exp_year = expense
        if exp_year == year and exp_month == month and exp_day <= day:
            monthly_expenses += amount

            target_category = category.split("::")[1] if "::" in category else category

            if target_category in expenses_by_category:
                expenses_by_category[target_category] += amount
            else:
                expenses_by_category[target_category] = amount

    return monthly_income, monthly_expenses, expenses_by_category


def stats(date_str):
    if not validate_date(date_str):
        print("Invalid date!")
        return

    day, month, year = parse_date(date_str)

    total_capital = calculate_total_capital(day, month, year)

    monthly_income, monthly_expenses, expenses_by_category = get_monthly_stats(day, month, year)

    profit_loss = monthly_income - monthly_expenses

    print(f"Your statistics as of {date_str}:")
    print(f"Total capital: {total_capital:.2f} rubles")

    if profit_loss >= 0:
        print(f"This month, the profit amounted to {profit_loss:.2f} rubles.")
    else:
        print(f"This month, the loss amounted to {abs(profit_loss):.2f} rubles.")

    print(f"Income: {monthly_income:.2f} rubles")
    print(f"Expenses: {monthly_expenses:.2f} rubles")

    if expenses_by_category:
        print("Details (category: amount):")
        sorted_categories = sorted(expenses_by_category.items())
        for i, (category, amount) in enumerate(sorted_categories, 1):
            print(f"{i}. {category}: {amount:.0f}")
    else:
        print("Details (category: amount):")


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
            add_income(amount_str, date_str)
        elif command == "cost":
            if len(parts) == 2 and parts[1] == "categories":
                print_available_categories()
            elif len(parts) == 4:
                category_name = parts[1]
                amount_str = parts[2]
                date_str = parts[3]
                add_expense(category_name, amount_str, date_str)
            else:
                print("Unknown command!")
        elif command == "stats" and len(parts) == 2:
            date_str = parts[1]
            stats(date_str)
        else:
            print("Unknown command!")
    except EOFError:
        break
