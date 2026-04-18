import json
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


class BreakerError(Exception):
    def __init__(
            self, func_name: str,
            block_time: datetime,
            source_exception: Exception | None = None
    ) -> None:
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
        errors = []

        if not isinstance(critical_count, int) or critical_count <= 0:
            errors.append(ValueError(INVALID_CRITICAL_COUNT))

        if not isinstance(time_to_recover, int) or time_to_recover <= 0:
            errors.append(ValueError(INVALID_RECOVERY_TIME))

        if errors:
            raise ExceptionGroup(VALIDATIONS_FAILED, errors)

        self.critical_count = critical_count
        self.time_to_recover = time_to_recover
        self.triggers_on = triggers_on

        self.errors_count: int = 0
        self.is_open: bool = False
        self.open_until: datetime
        self.func_name: str

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        self.func_name = f"{func.__module__}.{func.__name__}"

        @wraps(wrapped=func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            if self.is_open:
                cur_time = datetime.now(UTC)

                if self.open_until and cur_time >= self.open_until:
                    self.is_open = False
                    self.errors_count = 0
                else:
                    raise BreakerError(
                        self.func_name,
                        self.open_until,
                        None
                    )

            try:
                result = func(*args, **kwargs)
                self.errors_count = 0

            except Exception as e:
                if isinstance(e, self.triggers_on):
                    self.errors_count += 1

                    if self.errors_count >= self.critical_count:
                        self.is_open = True
                        right_time = datetime.now(UTC)
                        self.open_until = right_time + timedelta(seconds=self.time_to_recover)

                        raise BreakerError(
                            self.func_name,
                            right_time,
                            e
                        ) from e

                raise
            else:
                return result

        return wrapper



circuit_breaker = CircuitBreaker(5, 30, Exception)


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
