#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"
DIGITS = "0123456789"
LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

EXPENSE_CATEGORIES = {
	"Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
	"Transport": ("Taxi", "Public transport", "Gas", "Car service"),
	"Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
	"Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
	"Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
	"Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
	"Education": ("Courses", "Books", "Tutors"),
	"Communications": ("Mobile", "Internet", "Subscriptions"),
	"Other": ("SomeCategory", "SomeOtherCategory"),
}

REQUEST_TYPES = [
	"income",
	"cost",
	"stats"
]

MONTHS_DAYS = {
	1: 31,
	2: 28,
	3: 31,
	4: 30,
	5: 31,
	6: 30,
	7: 31,
	8: 31,
	9: 30,
	10: 31,
	11: 30,
	12: 31
}

financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
	"""
	Для заданного года определяет: високосный (True) или невисокосный (False).

	:param int year: Проверяемый год
	:return: Значение високосности.
	:rtype: bool
	"""
	return (year % 4 == 0) and (year % 100 != 0) or (year % 400 == 0)


def number_parser(num: str) -> float | None:
	if num == "":
		return None
	if num.count(".") + num.count(",") > 1:
		return None
	if num[0] == "-" or num[0] == "." or num[0] == ",":
		return None
	for i in range(len(num)):
		if not (num[i] in DIGITS or num[i] == "." or num[i] == ","):
			return None
	if num[-1] == "." or num[-1] == ",":
		return None
	num = num.replace(",", ".")
	return float(num)


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
	"""
	Парсит дату формата DD-MM-YYYY из строки.

	:param str maybe_dt: Проверяемая строка
	:return: typle формата (день, месяц, год) или None, если дата неправильная.
	:rtype: tuple[int, int, int] | None
	"""
	if len(maybe_dt) != 10:
		return None
	if maybe_dt[2] != "-" or maybe_dt[5] != "-":
		return None
	for i in (0, 1, 3, 4, 6, 7, 8, 9):
		if maybe_dt[i] not in DIGITS:
			return None
	date = tuple([int(maybe_dt[0:2]), int(maybe_dt[3:5]), int(maybe_dt[6:])])
	if is_leap_year(date[2]) and date[1] == 2 and date[0] <= 29:
		return date
	if date[1] < 1 or date[1] > 12:
		return None
	if date[0] > MONTHS_DAYS[date[1]]:
		return None
	return date


def to_str_date(date: list[int, int, int]) -> str:
	returner = ""
	for i in range(2):
		if len(str(date[i])) == 1:
			returner += "0"
		returner += str(date[i]) + "-"
	returner += str(date[2])
	return returner


def less_or_equal(date1: str, date2: str) -> bool:
	for i in [2, 1, 0]:
		if date1[i] < date2[i]:
			return True
		if date1[i] > date2[i]:
			return False
	return True


def category_parser(category: str) -> list[str] | None:
	if category.count(":") != 2 or category.count("::") != 1:
		return None
	for i in range(len(category)):
		if category[i] not in LETTERS and category[i] != ":":
			return None
	returner = category.split("::")
	if (returner[0] not in EXPENSE_CATEGORIES
		or returner[1] not in EXPENSE_CATEGORIES[returner[0]]):
		return None
	return returner


def income_request_parser(request_chopped: list[str]) -> dict | str:
	if len(request_chopped) != 3:
		return UNKNOWN_COMMAND_MSG
	amount = number_parser(request_chopped[1])
	if amount is None:
		return NONPOSITIVE_VALUE_MSG
	date = extract_date(request_chopped[2])
	if date is None:
		return INCORRECT_DATE_MSG
	return {"request_type": "income",
			"amount": amount,
			"date": date}


def cost_request_parser(request_chopped: list[str]) -> dict | str:
	if len(request_chopped) not in [2, 4]:
		return UNKNOWN_COMMAND_MSG
	if len(request_chopped) == 2 and request_chopped[1] == "categories":
		return {"request_type": "cost_categories"}
	category = category_parser(request_chopped[1])
	amount = number_parser(request_chopped[2])
	date = extract_date(request_chopped[3])
	if category is None:
		return NOT_EXISTS_CATEGORY
	if amount is None:
		return NONPOSITIVE_VALUE_MSG
	if date is None:
		return INCORRECT_DATE_MSG
	return {"request_type": "cost",
			"common_category": category[0],
			"target_category": category[1],
			"amount": amount,
			"date": date}


def stats_request_parser(request_chopped: list[str]) -> dict | str:
	if len(request_chopped) != 2:
		return UNKNOWN_COMMAND_MSG
	date = extract_date(request_chopped[1])
	if date is None:
		return INCORRECT_DATE_MSG
	return {"request_type": "stats",
			"date": date}


def request_parser(request: str) -> dict | str:
	request_chopped = request.split()
	if request_chopped[0] not in REQUEST_TYPES:
		return UNKNOWN_COMMAND_MSG
	if request_chopped[0] == "income":
		return income_request_parser(request_chopped)
	if request_chopped[0] == "cost":
		return cost_request_parser(request_chopped)
	if request_chopped[0] == "stats":
		return stats_request_parser(request_chopped)


def income_handler(amount: float, income_date: str) -> str:
	financial_transactions_storage.append({"request_type": "income",
										   "amount": amount,
										   "date": extract_date(income_date)})
	return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
	financial_transactions_storage.append({"request_type": "cost",
										   "category": category_name,
										   "amount": amount,
										   "date": extract_date(income_date)})
	return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
	returner = ""
	for elem in EXPENSE_CATEGORIES:
		for second_elem in EXPENSE_CATEGORIES[elem]:
			returner += f"{elem}::{second_elem}\n"
	return returner


def stats_handler(report_date: str) -> str:
	income = 0
	expenses = 0
	detailed_expenses = dict()
	for i in range(len(financial_transactions_storage)):
		element = financial_transactions_storage[i]
		if less_or_equal(element["date"], report_date):
			if element["request_type"] == "income":
				income += element["amount"]
			else:
				expenses += element["amount"]
				if element["category"] in detailed_expenses:
					detailed_expenses[element["category"]] += element["amount"]
				else:
					detailed_expenses[element["category"]] = element["amount"]

	total_capital = income - expenses

	returner = (f"Your statistics as of {report_date}:\n"
				f"Total capital: {total_capital} rubles\n")
	if total_capital > 0:
		returner += f"This month, the profit amounted to {total_capital} rubles.\n"
	else:
		returner += f"This month, the loss amounted to {total_capital} rubles.\n"
	returner += (f"Income: {income} rubles\n"
				 f"Expenses: {expenses} rubles\n\n"
				 f"Details (category: amount):\n")
	counter = 1
	for element in detailed_expenses:
		returner += f"{counter}. {element}: {detailed_expenses[element]}\n"
		counter += 1
	return returner


def main() -> None:
	inp = input()
	while inp:
		request = request_parser(inp)
		if isinstance(request, str):
			print(request)
		elif request["request_type"] == "income":
			print(income_handler(request["amount"],
								 to_str_date(request["date"])))
		elif request["request_type"] == "cost_categories":
			print(cost_categories_handler())
		elif request["request_type"] == "cost":
			print(cost_handler(request["common_category"] + "::" + request["target_category"],
							   request["amount"],
							   to_str_date(request["date"])))
		elif request["request_type"] == "stats":
			print(stats_handler(request["date"]))

		inp = input()


if __name__ == "__main__":
	main()
