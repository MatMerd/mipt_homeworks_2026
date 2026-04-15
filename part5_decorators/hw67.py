import json
from datetime import UTC, datetime
from functools import wraps
from typing import Any, ParamSpec, Protocol, TypeVar
from urllib.request import urlopen

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
    def __init__(self, message: str, func_name: str, block_time: datetime | None):
        self.func_name = func_name
        self.block_time = block_time
        super().__init__(message)


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 30,
        triggers_on: type[Exception] = Exception,
    ) -> None:
        exceptions = []
        if not isinstance(critical_count, int) or critical_count <= 0:
            exceptions.append(ValueError(INVALID_CRITICAL_COUNT))
        if not isinstance(time_to_recover, int) or time_to_recover <= 0:
            exceptions.append(ValueError(INVALID_RECOVERY_TIME))

        if exceptions:
            raise ExceptionGroup(VALIDATIONS_FAILED, exceptions)

        self.critical_count = critical_count
        self.time_to_recover = time_to_recover
        self.triggers_on = triggers_on

        self._failures = 0
        self.time_of_closure: datetime | None = None

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            block_time = self._activate_block()
            if block_time is not None:
                raise BreakerError(TOO_MUCH, self._get_func_name(func), block_time)

            try:
                return self._try_and_reset(func, *args, **kwargs)
            except self.triggers_on as error:
                self._handle_failure(func, error)
                raise

        return wrapper

    def _activate_block(self) -> datetime | None:
        if self.time_of_closure is None or self._failures < self.critical_count:
            return None
        time_passed = (datetime.now(UTC) - self.time_of_closure).total_seconds()
        if time_passed < self.time_to_recover:
            return self.time_of_closure
        self._failures = 0
        self.time_of_closure = None
        return None

    def _try_and_reset(self, func: CallableWithMeta[P, R_co], *args: P.args, **kwargs: P.kwargs) -> R_co:
        result = func(*args, **kwargs)
        self._failures = 0
        self.time_of_closure = None
        return result

    def _get_func_name(self, func: CallableWithMeta[P, R_co]) -> str:
        return f"{func.__module__}.{func.__name__}"

    def _handle_failure(self, func: CallableWithMeta[P, R_co], error: Exception) -> None:
        if self._failures + 1 >= self.critical_count:
            self._failures = self.critical_count
            self.time_of_closure = datetime.now(UTC)
            raise BreakerError(TOO_MUCH, self._get_func_name(func), self.time_of_closure) from error
        self._failures += 1


circuit_breaker = CircuitBreaker(5, 30, Exception)


# @circuit_breaker
def get_comments(post_id: int) -> Any:
    """
    Получает комментарии к посту

    Args:
        post_id (int): Идентификатор поста

    Returns:
        list[dict[int | str]]: Список комментариев
    """
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
