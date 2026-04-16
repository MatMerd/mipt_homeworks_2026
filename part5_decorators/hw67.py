import json
from datetime import UTC, datetime, timedelta
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
    def __init__(self, *, func_name: str, block_time: datetime):
        super().__init__(TOO_MUCH)
        self.func_name = func_name
        self.block_time = block_time


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int,
        time_to_recover: int,
        triggers_on: type[Exception],
    ):
        errors: list[ValueError] = []
        if isinstance(critical_count, bool) or not isinstance(critical_count, int) or critical_count <= 0:
            errors.append(ValueError(INVALID_CRITICAL_COUNT))
        if isinstance(time_to_recover, bool) or not isinstance(time_to_recover, int) or time_to_recover <= 0:
            errors.append(ValueError(INVALID_RECOVERY_TIME))
        if errors:
            raise ExceptionGroup(VALIDATIONS_FAILED, errors)

        self.critical_count = critical_count
        self.time_to_recover = time_to_recover
        self.triggers_on = triggers_on

        self._failed_count = 0
        self._blocked_until: datetime | None = None
        self._block_time: datetime | None = None

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            now = datetime.now(UTC)

            if self._blocked_until is not None:
                if now < self._blocked_until:
                    raise BreakerError(
                        func_name=f"{func.__module__}.{func.__name__}",
                        block_time=self._block_time,
                    )
                self._blocked_until = None
                self._block_time = None
                self._failed_count = 0

            try:
                result = func(*args, **kwargs)
            except Exception as error:
                if isinstance(error, self.triggers_on):
                    self._failed_count += 1
                    if self._failed_count >= self.critical_count:
                        block_time = datetime.now(UTC)
                        self._block_time = block_time
                        self._blocked_until = block_time + timedelta(seconds=self.time_to_recover)
                        self._failed_count = 0
                        raise BreakerError(
                            func_name=f"{func.__module__}.{func.__name__}",
                            block_time=block_time,
                        ) from error
                raise

            self._failed_count = 0
            return result

        return wrapper


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
