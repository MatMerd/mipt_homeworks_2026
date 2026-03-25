from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

from part4_oop.interfaces import Cache, HasCache, Policy, Storage

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class DictStorage(Storage[K, V]):
    _data: dict[K, V] = field(default_factory=dict, init=False)

    def set(self, key: K, value: V) -> None:
        raise NotImplementedError

    def get(self, key: K) -> V | None:
        raise NotImplementedError

    def exists(self, key: K) -> bool:
        raise NotImplementedError

    def remove(self, key: K) -> None:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError


@dataclass
class FIFOPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def register_access(self, key: K) -> None:
        raise NotImplementedError

    def get_key_to_evict(self) -> K | None:
        raise NotImplementedError

    def remove_key(self, key: K) -> None:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError

    @property
    def has_keys(self) -> bool:
        raise NotImplementedError


@dataclass
class LRUPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def register_access(self, key: K) -> None:
        raise NotImplementedError

    def get_key_to_evict(self) -> K | None:
        raise NotImplementedError

    def remove_key(self, key: K) -> None:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError

    @property
    def has_keys(self) -> bool:
        raise NotImplementedError


@dataclass
class LFUPolicy(Policy[K]):
    capacity: int = 5
    _key_counter: dict[K, int] = field(default_factory=dict, init=False)

    def register_access(self, key: K) -> None:
        raise NotImplementedError

    def get_key_to_evict(self) -> K | None:
        raise NotImplementedError

    def remove_key(self, key: K) -> None:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError

    @property
    def has_keys(self) -> bool:
        raise NotImplementedError


class MIPTCache(Cache[K, V]):
    def __init__(self, storage: Storage[K, V], policy: Policy[K]) -> None:
        self.storage = storage
        self.policy = policy

    def set(self, key: K, value: V) -> None:
        raise NotImplementedError

    def get(self, key: K) -> V | None:
        raise NotImplementedError

    def exists(self, key: K) -> bool:
        raise NotImplementedError

    def remove(self, key: K) -> None:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError


class CachedProperty[V]:
    def __init__(self, func: Callable[..., V]) -> None: ...
    def __get__(self, instance: HasCache[Any, Any] | None, owner: type) -> V: ...  # type: ignore[empty-body]
