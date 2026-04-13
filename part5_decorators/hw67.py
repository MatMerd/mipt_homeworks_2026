import json
import logging
from datetime import UTC, datetime
from functools import wraps
from typing import Any, ParamSpec, Protocol, TypeVar
from urllib.request import urlopen

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."

P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class CallableWithMeta(Protocol[P, R_co]):
    __name__: str
    __module__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...


class BreakerError(Exception):
    def __init__(self, msg: str, func: CallableWithMeta[Any, Any], block_time: datetime):
        super().__init__(msg)
        self.func_name = f"{func.__module__}.{func.__name__}"
        self.block_time = block_time


def _is_positive_integer(var: Any) -> bool:
    """Вспомогательная функция для валидации аргументов."""
    return isinstance(var, int) and var > 0


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 30,
        triggers_on: type[Exception] = Exception,
    ):
        exceptions = []
        if not _is_positive_integer(critical_count):
            exceptions.append(ValueError(INVALID_CRITICAL_COUNT))
        if not _is_positive_integer(time_to_recover):
            exceptions.append(ValueError(INVALID_RECOVERY_TIME))
        if exceptions:
            raise ExceptionGroup(VALIDATIONS_FAILED, exceptions)

        self.critical_count = critical_count
        self.time_to_recover = time_to_recover
        self.triggers_on = triggers_on
        self.counter = 0
        self.blocking_time: datetime | None = None

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            if self.blocking_time is not None:
                seconds_passed = (datetime.now(UTC) - self.blocking_time).total_seconds()
                if seconds_passed < self.time_to_recover:
                    raise BreakerError(TOO_MUCH, func, self.blocking_time)
                self.blocking_time = None

            return self._execute(func, *args, **kwargs)

        return wrapper

    def _execute(self, func: CallableWithMeta[P, R_co], *args: P.args, **kwargs: P.kwargs) -> R_co:
        try:
            result = func(*args, **kwargs)
        except self.triggers_on as exc:
            self.counter += 1
            if self.counter >= self.critical_count:
                self.counter = 0
                self.blocking_time = datetime.now(UTC)
                raise BreakerError(TOO_MUCH, func, self.blocking_time) from exc
            raise
        else:
            self.counter = 0
            return result


def get_comments(post_id: int) -> Any:
    """Получает комментарии к посту."""
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    try:
        comments = get_comments(1)
    except (RuntimeError, ValueError, BreakerError) as error:
        logger.exception("Caught error: %s", type(error).__name__)
    else:
        logger.info("Success! Got %d comments", len(comments))
