import json
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from functools import wraps
from typing import Any, ParamSpec, Protocol, TypeVar
from urllib.request import urlopen

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."

DEFAULT_CRITICAL_COUNT = 5
DEFAULT_RECOVERY_TIME = 30

P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class CallableWithMeta(Protocol[P, R_co]):
    __name__: str
    __module__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...


def validate_input(critical_count: int, time_to_recover: int) -> None:
    errors: list[Exception] = []

    if not isinstance(critical_count, int) or critical_count <= 0:
        errors.append(ValueError(INVALID_CRITICAL_COUNT))

    if not isinstance(time_to_recover, int) or time_to_recover <= 0:
        errors.append(ValueError(INVALID_RECOVERY_TIME))

    if errors:
        raise ExceptionGroup(VALIDATIONS_FAILED, errors)


class BreakerError(Exception):
    def __init__(self, func_name: str, block_time: datetime, source_exception: Exception | None = None) -> None:
        self.func_name = func_name
        self.block_time = block_time
        self.source_exception = source_exception
        super().__init__(TOO_MUCH)


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = DEFAULT_CRITICAL_COUNT,
        time_to_recover: int = DEFAULT_RECOVERY_TIME,
        triggers_on: type[Exception] = Exception,
    ) -> None:
        validate_input(critical_count, time_to_recover)
        self.critical_count = critical_count
        self.time_to_recover = time_to_recover
        self.triggers_on = triggers_on
        self._errors_count: int = 0
        self._is_open: bool = False
        self._open_until: datetime | None = None
        self._func_name: str = ""

    def _should_block(self) -> bool:
        if not self._is_open:
            return False

        cur_time = datetime.now(UTC)
        if self._open_until and cur_time >= self._open_until:
            self._is_open = False
            self._errors_count = 0
            return False
        return True

    def _notice_error(self, error: Exception) -> None:
        self._errors_count += 1
        if self._errors_count >= self.critical_count:
            self._is_open = True
            right_time = datetime.now(UTC)
            self._open_until = right_time + timedelta(seconds=self.time_to_recover)
            raise BreakerError(self._func_name, right_time, error) from error
        raise error

    def __call__(self, func: CallableWithMeta[P, R_co]) -> Callable[..., R_co]:
        self._func_name = f"{func.__module__}.{func.__name__}"

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            if self._should_block():
                if self._open_until is None:
                    raise BreakerError(self._func_name, datetime.now(UTC), None)
                raise BreakerError(self._func_name, self._open_until, None)
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                if isinstance(e, self.triggers_on):
                    self._notice_error(e)
                raise
            else:
                self._errors_count = 0
                return result

        return wrapper


circuit_breaker = CircuitBreaker(5, 30, Exception)


def get_comments(post_id: int) -> Any:
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
