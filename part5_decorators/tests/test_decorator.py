from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock

import pytest
from freezegun import freeze_time

from part5_decorators.hw67 import (
    TOO_MUCH,
    VALIDATIONS_FAILED,
    BreakerError,
    CircuitBreaker,
    get_comments,
)


@pytest.mark.parametrize(
    ("critical_count", "time_to_recover", "exceptions"),
    [
        (-1, 5, (ValueError,)),
        (0, 5, (ValueError,)),
        (1, -1, (ValueError,)),
        (1, 0, (ValueError,)),
        (0, 0, (ValueError, ValueError)),
        (-1, -1, (ValueError, ValueError)),
    ],
)
def test_validation(
    critical_count: int,
    time_to_recover: int,
    exceptions: tuple[type[Exception], ...],
    mock_urlopen: MagicMock,
) -> None:
    """Проверяет валидацию аргументов декоратора"""
    mock_urlopen.return_value = None
    with pytest.RaisesGroup(*exceptions, match=VALIDATIONS_FAILED):
        CircuitBreaker(critical_count, time_to_recover, Exception)(get_comments)(1)


@pytest.mark.parametrize(
    ("args", "kwargs"),
    [((), {"post_id": 99}), ((99,), {})],
)
def test_args_kwargs(
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    mock_urlopen: MagicMock,
) -> None:
    """Проверяет проброс аргументов до функции"""
    CircuitBreaker(5, 5, Exception)(get_comments)(*args, **kwargs)
    mock_urlopen.assert_called_once_with("https://jsonplaceholder.typicode.com/comments?postId=99")


def test_block(mock_urlopen: MagicMock) -> None:
    """Проверка блокировки автомата"""
    mock_urlopen.side_effect = TimeoutError()
    decorated = CircuitBreaker(2, 30, TimeoutError)(get_comments)
    with pytest.raises(TimeoutError):
        decorated(123)
    with pytest.raises(BreakerError, match=TOO_MUCH):
        decorated(123)


def test_block_disables_call(mock_urlopen: MagicMock) -> None:
    """Проверка, что после срабатывания автомата вызовы не идут"""
    mock_urlopen.side_effect = TimeoutError()
    decorated = CircuitBreaker(1, 30, TimeoutError)(get_comments)
    with pytest.raises(BreakerError, match=TOO_MUCH):
        decorated(124)
    with pytest.raises(BreakerError, match=TOO_MUCH):
        decorated(124)
    mock_urlopen.assert_called_once_with("https://jsonplaceholder.typicode.com/comments?postId=124")


def test_block_unlock(mock_urlopen: MagicMock) -> None:
    """Проверка, что успешный запрос сбрасывает счётчик ошибок"""
    mock_urlopen.return_value.read.side_effect = [TimeoutError(), b"[]", TimeoutError()]
    decorated = CircuitBreaker(2, 30, TimeoutError)(get_comments)
    with pytest.raises(TimeoutError):
        decorated(125)
    decorated(125)
    with pytest.raises(TimeoutError):
        decorated(125)


def test_original_attributes() -> None:
    decorated = CircuitBreaker(1, 2, TimeoutError)(get_comments)
    assert decorated.__name__ == get_comments.__name__
    assert decorated.__doc__ == get_comments.__doc__


@pytest.mark.parametrize(
    ("seconds", "expected_work"),
    [(29, False), (30, True), (31, True)],
)
def test_recovery(seconds: int, *, expected_work: bool, mock_urlopen: MagicMock) -> None:
    """Проверяет отмену блокировки по истечении recovery_time"""
    mock_urlopen.return_value.read.side_effect = [TimeoutError(), TimeoutError(), b"[]"]
    decorated = CircuitBreaker(2, 30, TimeoutError)(get_comments)
    with freeze_time("2026-05-15 10:00:00") as frozen_time:
        with pytest.raises(TimeoutError):
            decorated(126)
        with pytest.raises(BreakerError, match=TOO_MUCH):
            decorated(126)
        frozen_time.move_to(f"2026-05-15 10:00:{seconds}")
        if expected_work:
            decorated(126)
        else:
            with pytest.raises(BreakerError, match=TOO_MUCH):
                decorated(126)


def test_error_structure(mock_urlopen: MagicMock) -> None:
    """Проверяет атрибуты исключения BreakerError и источники"""
    break_error = TimeoutError()

    def check_breaker_error(error: BreakerError) -> bool:
        return (
            error.__cause__ == break_error
            and getattr(error, "func_name", None) == "part5_decorators.hw67.get_comments"
            and getattr(error, "block_time", None) == datetime(2026, 5, 15, 10, tzinfo=UTC)
        )

    mock_urlopen.return_value.read.side_effect = break_error
    decorated = CircuitBreaker(1, 30, TimeoutError)(get_comments)
    with freeze_time("2026-05-15 10:00:00"):
        with pytest.raises(BreakerError, check=check_breaker_error):
            decorated(127)
        with pytest.raises(BreakerError, check=lambda ex: ex.__cause__ is None):
            decorated(127)


@pytest.mark.parametrize(
    "internal_error",
    [OSError, ValueError, IndexError, TypeError, KeyError],
)
def test_error_filtering(internal_error: type[Exception], mock_urlopen: MagicMock) -> None:
    """Проверяет фильтрацию по типу из triggers_on"""
    mock_urlopen.return_value.read.side_effect = [TimeoutError, internal_error, TimeoutError]
    decorated = CircuitBreaker(2, 30, TimeoutError)(get_comments)
    with freeze_time("2026-05-15 10:00:00"):
        with pytest.raises(TimeoutError):
            decorated(128)
        with pytest.raises(internal_error):
            decorated(128)
        with pytest.raises(BreakerError):
            decorated(128)
