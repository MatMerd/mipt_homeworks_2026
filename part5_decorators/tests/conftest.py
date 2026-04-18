from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture


@pytest.fixture
def mock_urlopen(mocker: MockerFixture) -> MagicMock:
    urlopen_mock = mocker.patch("part5_decorators.hw67.urlopen")
    response_mock = mocker.MagicMock()
    response_mock.read.return_value = b"[]"
    urlopen_mock.return_value = response_mock
    return urlopen_mock
