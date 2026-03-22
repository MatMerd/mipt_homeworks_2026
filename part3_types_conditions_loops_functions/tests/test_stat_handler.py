from collections.abc import Callable
from datetime import datetime

import pytest

from part3_types_conditions_loops_functions.hw3 import stats_handler
from part3_types_conditions_loops_functions.tests.conftest import DATE_FORMAT


@pytest.mark.optional
def test_stats_output(fill_financial_storage_date: datetime, assert_stats_result: Callable[..., None]) -> None:
    result = stats_handler(fill_financial_storage_date.strftime(DATE_FORMAT))
    assert_stats_result(result, fill_financial_storage_date)
