import json
from dataclasses import dataclass
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
    def __init__(self, func_name: str, block_time: datetime):
        super().__init__(TOO_MUCH)
        self.func_name = func_name
        self.block_time = block_time


@dataclass
class _BreakerState:
    consecutive_failures: int = 0
    blocked_until: datetime | None = None
    block_time: datetime | None = None


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 30,
        triggers_on: type[Exception] = Exception,
    ):
        self._critical_count = critical_count
        self._time_to_recover = time_to_recover
        self._triggers_on = triggers_on
        self._validate()

    def __call__(
        self,
        func: CallableWithMeta[P, R_co],
    ) -> CallableWithMeta[P, R_co]:
        state = _BreakerState()
        func_name = f"{func.__module__}.{func.__name__}"

        @wraps(func)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> R_co:
            now = datetime.now(UTC)
            self._raise_if_blocked(state, now, func_name)
            self._recover_if_ready(state, now)

            try:
                result = func(*args, **kwargs)
            except self._triggers_on as error:
                self._handle_trigger_error(state, error, func_name)
                raise
            state.consecutive_failures = 0
            return result

        return wrapped

    def _validate(self) -> None:
        errors: list[ValueError] = []
        if not isinstance(self._critical_count, int) or self._critical_count <= 0:
            errors.append(ValueError(INVALID_CRITICAL_COUNT))
        if not isinstance(self._time_to_recover, int) or self._time_to_recover <= 0:
            errors.append(ValueError(INVALID_RECOVERY_TIME))
        if errors:
            raise ExceptionGroup(VALIDATIONS_FAILED, errors)

    def _create_breaker_error(
        self,
        func_name: str,
        block_time: datetime,
    ) -> BreakerError:
        return BreakerError(func_name=func_name, block_time=block_time)

    def _raise_if_blocked(
        self,
        state: _BreakerState,
        now: datetime,
        func_name: str,
    ) -> None:
        if state.blocked_until is None or now >= state.blocked_until:
            return
        if state.block_time is None:
            state.block_time = now
        raise self._create_breaker_error(func_name, state.block_time)

    def _recover_if_ready(self, state: _BreakerState, now: datetime) -> None:
        if state.blocked_until is None or now < state.blocked_until:
            return
        state.blocked_until = None
        state.block_time = None
        state.consecutive_failures = 0

    def _handle_trigger_error(
        self,
        state: _BreakerState,
        error: Exception,
        func_name: str,
    ) -> None:
        state.consecutive_failures += 1
        if state.consecutive_failures < self._critical_count:
            return
        block_time = datetime.now(UTC)
        state.block_time = block_time
        state.blocked_until = block_time + timedelta(
            seconds=self._time_to_recover,
        )
        state.consecutive_failures = 0
        raise self._create_breaker_error(func_name, block_time) from error


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
    response = urlopen(
        f"https://jsonplaceholder.typicode.com/comments?postId={post_id}",
    )
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
