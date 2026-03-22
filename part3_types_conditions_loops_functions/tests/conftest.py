from collections import defaultdict
from collections.abc import Callable, Generator
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from typing import NotRequired, Protocol, TypedDict, TypeVar, Unpack

import pytest
from faker import Faker
from polyfactory.factories import DataclassFactory
from polyfactory.pytest_plugin import register_fixture

from part3_types_conditions_loops_functions import hw3

DATE_FORMAT = "%d-%m-%Y"
STATS_TEMPLATE = """Your statistics as of {stats_date}:
Total capital: {total_capital} rubles
This month, the {amount_word} amounted to {total_capital} rubles.
Income: {costs_amount} rubles
Expenses: {incomes_amount} rubles

Details (category: amount):
{category_details_stat}
"""


def pytest_addoption(parser) -> None:  # type: ignore[no-untyped-def]
    parser.addoption("--run-optional", action="store_true", default=False, help="run optional tests")


def pytest_configure(config) -> None:  # type: ignore[no-untyped-def]
    config.addinivalue_line("markers", "optional: mark test as optional to run")


def pytest_collection_modifyitems(config, items) -> None:  # type: ignore[no-untyped-def]
    if config.getoption("--run-optional"):
        # --run-optional given in cli: do not skip slow tests
        return
    skip_optional = pytest.mark.skip(reason="need --run-optional option to run")
    for item in items:
        if "optional" in item.keywords:
            item.add_marker(skip_optional)


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
    def __call__(self, **kwargs: Unpack[IncomeKwargs]) -> S_co: ...


class CostBuilder[S_co](Protocol):
    def __call__(self, **kwargs: Unpack[CostKwargs]) -> S_co: ...


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


@pytest.fixture
def incomes_batch(income_factory: type[IncomeFactory]) -> Generator[list[Income]]:
    yield income_factory.batch(3)


@pytest.fixture
def costs_batch(cost_factory: type[CostFactory]) -> Generator[list[Cost]]:
    yield cost_factory.batch(3)


@pytest.fixture
def fill_financial_storage_date(incomes_batch: list[Income], costs_batch: list[Cost]) -> datetime:
    base_date = datetime.now(UTC) - timedelta(days=3)

    for i, income in enumerate(incomes_batch):
        cost = costs_batch[i]
        str_date = base_date.strftime(DATE_FORMAT)
        income.date = str_date
        cost.date = str_date
        hw3.financial_transactions_storage.extend((asdict(income), asdict(cost)))
        base_date += timedelta(days=1)
    return base_date


@pytest.fixture
def assert_stats_result(incomes_batch: list[Income], costs_batch: list[Cost]) -> Callable[..., None]:
    def inner_assert(stats_result: str, stats_date: datetime) -> None:
        costs_amount = round(
            sum(
                cost.amount
                for cost in costs_batch
                if datetime.strptime(cost.date, DATE_FORMAT).replace(tzinfo=UTC) < stats_date
            ),
            2,
        )
        incomes_amount = round(
            sum(
                income.amount
                for income in incomes_batch
                if datetime.strptime(income.date, DATE_FORMAT).replace(tzinfo=UTC) < stats_date
            ),
            2,
        )
        total_capital = round(costs_amount - incomes_amount, 2)
        category_details: defaultdict[str, float] = defaultdict(float)
        category_details_stat_data = []
        for i, cost in enumerate(costs_batch, 1):
            category_details[cost.category] += cost.amount
            category_details_stat_data.append(f"{i}. {cost.category}: {cost.amount}")
        category_details_stat = "\n".join(category_details_stat_data)
        amount_word = "loss" if total_capital < 0 else "profit"
        stats = STATS_TEMPLATE.format_map(
            {
                "stats_date": stats_date.strftime(DATE_FORMAT),
                "total_capital": total_capital,
                "amount_word": amount_word,
                "costs_amount": costs_amount,
                "incomes_amount": incomes_amount,
                "category_details_stat": category_details_stat,
            }
        )
        assert stats == stats_result

    return inner_assert
