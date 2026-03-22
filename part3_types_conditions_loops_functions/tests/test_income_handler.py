from part3_types_conditions_loops_functions import hw3
from part3_types_conditions_loops_functions.tests.conftest import Income, IncomeBuilder, parse_date


def test_income_success(valid_income: Income) -> None:
    result = hw3.income_handler(valid_income.amount, valid_income.date)
    income_data = hw3.financial_transactions_storage[-1]
    assert result == hw3.OP_SUCCESS_MSG
    assert income_data
    assert income_data["amount"] == valid_income.amount
    assert income_data["date"] == parse_date(valid_income.date)


def test_income_amount_less_than_zero(invalid_income_factory: IncomeBuilder[Income]) -> None:
    invalid_income = invalid_income_factory(amount=-1)
    result = hw3.income_handler(invalid_income.amount, invalid_income.date)
    income_data = hw3.financial_transactions_storage[-1]
    assert result == hw3.NONPOSITIVE_VALUE_MSG
    assert not income_data


def test_income_invalid_date(invalid_income_factory: IncomeBuilder[Income]) -> None:
    invalid_income = invalid_income_factory(date="invalid")
    result = hw3.income_handler(invalid_income.amount, invalid_income.date)
    income_data = hw3.financial_transactions_storage[-1]
    assert result == hw3.INCORRECT_DATE_MSG
    assert not income_data
