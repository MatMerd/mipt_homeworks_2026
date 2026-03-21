from collections.abc import Generator
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import NotRequired, Protocol, TypedDict, TypeVar, Unpack

import pytest
from faker import Faker
from polyfactory.factories import DataclassFactory
from polyfactory.pytest_plugin import register_fixture

from part3_types_conditions_loops_functions import hw3

DATE_FORMAT = "%d-%m-%Y"


def parse_date(raw_date: str) -> tuple[int, int, int]:
    date_object = datetime.strptime(raw_date, DATE_FORMAT).replace(tzinfo=UTC)
    return date_object.day, date_object.month, date_object.year


@dataclass
class Income:
    amount: float
    date: str


@dataclass
class Cost:
    amount: float
    date: str
    category: str


class IncomeKwargs(TypedDict):
    amount: NotRequired[float]
    date: NotRequired[str]


class CostKwargs(TypedDict):
    amount: NotRequired[float]
    date: NotRequired[str]
    category: NotRequired[str]


S_co = TypeVar("S_co", covariant=True)


class IncomeBuilder[S_co](Protocol):
    def __call__(self, **kwargs: Unpack[IncomeKwargs]) -> S_co:
        ...


class CostBuilder[S_co](Protocol):
    def __call__(self, **kwargs: Unpack[CostKwargs]) -> S_co:
        ...


@register_fixture
class IncomeFactory(DataclassFactory[Income]):
    __faker__ = Faker("en_US")

    @classmethod
    def amount(cls) -> float:
        return float(cls.__faker__.pydecimal(5, 2, positive=True))

    @classmethod
    def date(cls) -> str:
        return datetime.now(tz=UTC).strftime(DATE_FORMAT)


@register_fixture
class CostFactory(DataclassFactory[Cost]):
    __faker__ = Faker("en_US")

    @classmethod
    def amount(cls) -> float:
        return float(cls.__faker__.pydecimal(5, 2, positive=True))

    @classmethod
    def date(cls) -> str:
        return datetime.now(tz=UTC).strftime(DATE_FORMAT)

    @classmethod
    def category(cls) -> str:
        random_common_category: str = cls.__random__.choice(tuple(hw3.EXPENSE_CATEGORIES.keys()))
        random_target_category = cls.__random__.choice(hw3.EXPENSE_CATEGORIES[random_common_category])
        return f"{random_common_category}::{random_target_category}"


@pytest.fixture(autouse=True)
def setup_financial_storage() -> Generator[None]:
    old_storage_data = hw3.financial_transactions_storage
    hw3.financial_transactions_storage = []
    yield
    hw3.financial_transactions_storage = old_storage_data


@pytest.fixture
def valid_income(income_factory: type[IncomeFactory]) -> Income:
    return income_factory.build()


@pytest.fixture
def invalid_income_factory(income_factory: type[IncomeFactory]) -> IncomeBuilder[Income]:
    def builder(**kwargs: Unpack[IncomeKwargs]) -> Income:
        return income_factory.build(**kwargs)

    return builder


@pytest.fixture
def valid_cost(cost_factory: type[CostFactory]) -> Cost:
    return cost_factory.build()


@pytest.fixture
def invalid_cost_factory(cost_factory: type[CostFactory]) -> CostBuilder[Cost]:
    def builder(**kwargs: Unpack[CostKwargs]) -> Cost:
        return cost_factory.build(**kwargs)

    return builder
