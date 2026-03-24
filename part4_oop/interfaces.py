from collections.abc import Callable
from typing import Any, Protocol, TypeVar

K_contra = TypeVar("K_contra", contravariant=True)
K = TypeVar("K")
V = TypeVar("V")


class BaseStorage(Protocol[K_contra, V]):
    def set(self, key: K_contra, value: V) -> None: ...
    def get(self, key: K_contra) -> V | None: ...
    def exists(self, key: K_contra) -> bool: ...
    def remove(self, key: K_contra) -> None: ...
    def clear(self) -> None: ...


class BasePolicy(Protocol[K]):
    def register_access(self, key: K) -> None: ...
    def get_key_to_evict(self) -> K | None: ...


class Cache(Protocol[K_contra, V]):
    def __init__(
        self,
        storage: BaseStorage[K_contra, V],
        policy: BasePolicy[K_contra],
        capacity: int,
    ) -> None: ...
    def set(self, key: K_contra, value: V) -> None: ...
    def get(self, key: K_contra) -> V | None: ...


class HasCache(Protocol[K, V]):
    cache: Cache[K, V]


class CachedProperty[V]:
    def __init__(self, func: Callable[..., V]) -> None: ...
    def __get__(self, instance: HasCache[Any, Any] | None, owner: type) -> V: ...  # type: ignore[empty-body]
