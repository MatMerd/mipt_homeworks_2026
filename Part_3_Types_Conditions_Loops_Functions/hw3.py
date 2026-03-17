#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"

global all_transactions
all_transactions = [0,[],[]]
def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """

    if year % 4 == 0 and year % 100 != 0:
        return True
    elif year % 400 == 0:
        return True
    return False


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    if maybe_dt is None:
        return None
    if len(maybe_dt.split("-")) != 3:
        return None
    if "--" in maybe_dt or maybe_dt[0] == "-" or maybe_dt[-1] == "-" or "---" in maybe_dt:
        return None
    for char in maybe_dt:
        if char not in "0123456789-":
            return None
    maybe_dt = maybe_dt.split("-")
    day = int(maybe_dt[0])
    month = int(maybe_dt[1])
    year = int(maybe_dt[2])
    
    if (day < 1 or day > 31 or month < 1 or month > 12):
        return None
    
    elif day >= 31 and month in [4, 6, 9, 11]:
        return None
    
    elif is_leap_year(year) == False and month == 2 and day == 29:
        return None

    elif month == 2 and day > 29:
        return None

    return day, month, year


def income_handler(amount: float, income_date: str) -> str:
    # all_transactions = [0,[],[]]
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG
    all_transactions[1].append([amount, income_date])
    all_transactions[0] += amount
    return f"{OP_SUCCESS_MSG} {amount=} {income_date=}"

def cost_handler(category: str, amount: float, cost_date: str) -> str:
    # all_transactions = [0,[],[]]
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG
    all_transactions[2].append([category, amount, cost_date])
    all_transactions[0] -= amount
    return f"{OP_SUCCESS_MSG} {category=} {amount=} {cost_date=}"

def stats_handler(date: str) -> tuple[float, float, float, list] | str:
    # all_transactions = [0,[],[]]
    # capital = all_transactions[0]
    capital = sum([profit_in_curr_transaction[0] for profit_in_curr_transaction in all_transactions[1]]) - sum([loss_in_curr_transaction[1] for loss_in_curr_transaction in all_transactions[2]])
    loss = sum([loss_in_curr_transaction[1] for loss_in_curr_transaction in all_transactions[2] if 
                extract_date(loss_in_curr_transaction[2])[2] == extract_date(date)[2] and extract_date(loss_in_curr_transaction[2])[1] == extract_date(date)[1]])
    profit = sum([profit_in_curr_transaction[0] for profit_in_curr_transaction in all_transactions[1] if
                  extract_date(profit_in_curr_transaction[1])[2] == extract_date(date)[2] and extract_date(profit_in_curr_transaction[1])[1] == extract_date(date)[1]])
    # profit_list = [profit_in_curr_transaction for profit_in_curr_transaction in all_transactions[1] if
    #               extract_date(profit_in_curr_transaction[1])[2] == extract_date(date)[2]]
    loss_list = [loss_in_curr_transaction for loss_in_curr_transaction in all_transactions[2] if
                extract_date(loss_in_curr_transaction[2])[2] == extract_date(date)[2] and extract_date(loss_in_curr_transaction[2])[1] == extract_date(date)[1]]

    dict_of_categories = {}
    for loss_transaction in loss_list:
        category = loss_transaction[0]
        if category not in dict_of_categories:
            dict_of_categories[category] = 0
        dict_of_categories[category] += loss_transaction[1]
    list_of_categories = list(dict_of_categories.items())
    list_of_categories.sort(key=lambda loss_transaction: loss_transaction[0])
    return capital, loss, profit, list_of_categories

def sum_into_float(maybe_float: str) -> float:
    for char in maybe_float:
        if char not in "0123456789,.":
            return None
    for char in maybe_float:
        if char in ".,": 
            if maybe_float.count(char) > 1:
                return None
    if "." in maybe_float or maybe_float.count(",") + maybe_float.count(".") == 0:
        return float(maybe_float)
    return float(f"{maybe_float.split(',')[0]}.{maybe_float.split(',')[1]}")

def main() -> None:
    """Ваш код здесь"""
    while True:
        command = input()
        if len(command.split()) < 1:
            print(UNKNOWN_COMMAND_MSG)
        elif len(command.split()) > 4:
            print(UNKNOWN_COMMAND_MSG)
        elif len(command.split()) == 3:
            if command.split()[0] == "income":
                if sum_into_float(command.split()[1]) is None:
                    print(UNKNOWN_COMMAND_MSG)
                elif sum_into_float(command.split()[1]) <= 0:
                    print(NONPOSITIVE_VALUE_MSG)
                elif extract_date(command.split()[2]) is None:
                    print(INCORRECT_DATE_MSG)
                else:
                    res = income_handler(sum_into_float(command.split()[1]), command.split()[2])
                    if res[0] == "A":
                        print(OP_SUCCESS_MSG)
        elif len(command.split()) == 4:
            if command.split()[0] == "cost":
                if sum_into_float(command.split()[2]) is None:
                    print(UNKNOWN_COMMAND_MSG)
                elif sum_into_float(command.split()[2]) <= 0:
                    print(NONPOSITIVE_VALUE_MSG)
                elif extract_date(command.split()[3]) is None:
                    print(INCORRECT_DATE_MSG)

                else:
                    res = cost_handler(command.split()[1], sum_into_float(command.split()[2]), command.split()[3])
                    if res[0] == "A":
                        print(OP_SUCCESS_MSG)
                        
        elif len(command.split()) == 2:
            if command.split()[0] == "stats":
                if extract_date(command.split()[1]) is None:
                    print(INCORRECT_DATE_MSG)
                else:
                    date = command.split()[1]
                    stats_info = stats_handler(date)
                    details = "\n".join(
                        f"{i}. {category}: {amount}"
                        for i, (category, amount) in enumerate(stats_info[3], start=1)
                    )
                    if details == "":
                        if stats_info[2] - stats_info[1] >= 0:
                            print(
                            f"Your statistics as of {date}:\n"
                            f"Total capital: {stats_info[0]} rubles\n"
                            f"This month's profit: {stats_info[2] - stats_info[1]} rubles\n"
                            f"Income: {stats_info[2]} rubles\n"
                            f"Expenses: {stats_info[1]} rubles\n\n"
                            f"Breakdown (category: amount):")
                        else:
                            print(
                            f"Your statistics as of {date}:\n"
                            f"Total capital: {stats_info[0]} rubles\n"
                            f"This month's loss: {stats_info[1] - stats_info[2]} rubles\n"
                            f"Income: {stats_info[2]} rubles\n"
                            f"Expenses: {stats_info[1]} rubles\n\n"
                            f"Breakdown (category: amount):")
                    else:
                        if stats_info[2] - stats_info[1] >= 0:
                            print(
                            f"Your statistics as of {date}:\n"
                            f"Total capital: {stats_info[0]} rubles\n"
                            f"This month's profit: {stats_info[2] - stats_info[1]} rubles\n"
                            f"Income: {stats_info[2]} rubles\n"
                            f"Expenses: {stats_info[1]} rubles\n\n"
                            f"Breakdown (category: amount):\n{details}")
                        else:
                            print(
                            f"Your statistics as of {date}:\n"
                            f"Total capital: {stats_info[0]} rubles\n"
                            f"This month's loss: {stats_info[1] - stats_info[2]} rubles\n"
                            f"Income: {stats_info[2]} rubles\n"
                            f"Expenses: {stats_info[1]} rubles\n\n"
                            f"Breakdown (category: amount):\n{details}")
        else:
            print(UNKNOWN_COMMAND_MSG)            
                
if __name__ == "__main__":
    main()
