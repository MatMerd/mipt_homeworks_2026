#!/usr/bin/env python

income_dict: dict[tuple[int, int, int], int | float] = {}
expence_dict: dict[tuple[int, int, int], int | float] = {}
details_dict: dict[tuple[int, int, int], dict[str, int | float]] = {}
months = [4, 6, 9, 11]
UNKNOWN_COMMAND_MSG = "Неизвестная команда!"
NONPOSITIVE_VALUE_MSG = "Значение должно быть больше нуля!"
INCORRECT_DATE_MSG = "Неправильная дата!"
OP_SUCCESS_MSG = "Добавлено"

def income(amount: int | float, date: str):
        if amount > 0:
            tuple_date = extract_data(date)
            if not tuple_date is None:
                if not tuple_date in income_dict.keys():
                    income_dict[tuple_date] = 0
                income_dict[tuple_date] += amount
                print(OP_SUCCESS_MSG)
                return
            print(INCORRECT_DATE_MSG)
            return
        print(NONPOSITIVE_VALUE_MSG)
        return
    
def cost(category_name: str, amount: int | float, date: str):
    if amount > 0:
        tuple_date = extract_data(date)
        if not tuple_date is None:
            if not date in expence_dict.keys():
                expence_dict[tuple_date], details_dict[tuple_date] = 0, dict()
            expence_dict[tuple_date] += amount
            if not category_name in details_dict[tuple_date].keys():
                details_dict[tuple_date][category_name] = 0
            details_dict[tuple_date][category_name] += amount
            print(OP_SUCCESS_MSG)
            return
        print(INCORRECT_DATE_MSG)
        return
    print(NONPOSITIVE_VALUE_MSG)
    return

def stats(date: str):
    tuple_date = extract_data(date)
    if not tuple_date is None:
        income, account, expence, k = 0, 0, 0, 1
        categories: dict[str, int | float] = {}
        for el in income_dict.keys():
            if compare_date(tuple_date, el) and tuple_date[1:] == el[1:]:
                account += income_dict[el]
                income += income_dict[el]
        for el in expence_dict.keys():
            if compare_date(tuple_date, el) and tuple_date[1:] == el[1:]:
                account -= expence_dict[el]
                expence += expence_dict[el]
                categories.update(details_dict[el])
        sorted_categories = dict(sorted(categories.items(), key=lambda el: el[0]))
        print(f'''Ваша статистика по состоянию на {date}:
Суммарный капитал: {account:.2f} рублей
В этом месяце {("прибыль составила", "убыток составил")[0 if income - expence >= 0 else 1]} {income - expence:.2f} рублей 
Доходы: {income:.2f} рублей
Расходы: {expence:.2f} рублей

Детализация (категория: сумма):''')
        for i in sorted_categories.keys():
            print(f"{k}. {i}: {sorted_categories[i]}")
            k += 1

def compare_date(first: tuple[int, int, int], second: tuple[int, int, int]):
    fday, fmonth, fyear = first[0], first[1], first[2]
    sday, smonth, syear = second[0], second[1], second[2]
    if fday >= sday:
        if fmonth >= smonth:
            if fyear >= syear:
                return True
    return False

def date_validation(day: int, month: int, year: int):
    if month in months:
        return 1 <= day <= 30
    elif month == 2:
        if is_leap_year(year):
            return 1 <= day <= 29
        else:
            return 1 <= day <= 28
    elif 1 <= month <= 12:
        return 1 <= day <= 31
    return False

def main() -> None:
    input_line = input().split()
    command = input_line[0]
    match command:
        case "income":
            if len(input_line) == 3:
                income(int(input_line[1]), input_line[2])
            else:
                print(UNKNOWN_COMMAND_MSG)
        case "cost":
            if len(input_line) == 4:
                cost(input_line[1], int(input_line[2]), input_line[3])
            else:
                print(UNKNOWN_COMMAND_MSG)
        case "stats":
            if len(input_line) == 2:
                stats(input_line[1])
            else:
                print(UNKNOWN_COMMAND_MSG)
                
    
def is_leap_year(year: int) -> bool:
    if (not year % 2 and year % 2) or (not year % 400):
        return True
    return False

def extract_data(maybe_dt: str) -> tuple[int, int, int] | None:
    if len(maybe_dt) == 10:
        day, month, year = map(int, maybe_dt.split("-"))
        if date_validation(day, month, year):
            return (day, month, year)     

if __name__ == "__main__":
    main()
    
