import json
from dataclasses import dataclass
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


@dataclass
class BreakerState:
    count: int = 0
    block_time: datetime | None = None


class CallableWithMeta(Protocol[P, R_co]):
    __name__: str
    __module__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...


class BreakerError(Exception):
    def __init__(self, func_name: str | None = None, block_time: datetime | None = None):
        super().__init__(TOO_MUCH)
        self.func_name = func_name
        self.block_time = block_time


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 30,
        triggers_on: type[Exception] = Exception,
    ):
        errors: list[ValueError] = []
        if not isinstance(critical_count, int) or critical_count <= 0:
            errors.append(ValueError(INVALID_CRITICAL_COUNT))
        if not isinstance(time_to_recover, int) or time_to_recover <= 0:
            errors.append(ValueError(INVALID_RECOVERY_TIME))
        if errors:
            raise ExceptionGroup(VALIDATIONS_FAILED, errors)

        self.critical_count = critical_count
        self.time_to_recover = time_to_recover
        self.triggers_on = triggers_on
        self.count = 0

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        func_name = f"{func.__module__}.{func.__name__}"
        state = BreakerState()

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            if state.block_time is not None:
                if (datetime.now(UTC) - state.block_time).total_seconds() < self.time_to_recover:
                    raise BreakerError(func_name, state.block_time)
                state.block_time = None
                state.count = 0
            return self.helper(func, func_name, state, *args, **kwargs)

        return wrapper

    def helper(
        self,
        func: CallableWithMeta[P, R_co],
        func_name: str,
        state: BreakerState,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R_co:
        try:
            result = func(*args, **kwargs)
        except self.triggers_on as err:
            state.count += 1
            if state.count < self.critical_count:
                raise
            state.block_time = datetime.now(UTC)
            raise BreakerError(func_name, state.block_time) from err
        state.count = 0
        state.block_time = None
        return result


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
