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
        self._data[key] = value

    def get(self, key: K) -> V | None:
        if self.exists(key):
            return self._data[key]
        return None

    def exists(self, key: K) -> bool:
        return key in self._data

    def remove(self, key: K) -> None:
        if self.exists(key):
            self._data.pop(key, None)

    def clear(self) -> None:
        self._data.clear()


@dataclass
class FIFOPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def __init__(self, capacity: int = 5) -> None:
        self._order = []
        self.capacity = capacity

    def register_access(self, key: K) -> None:
        if key not in self._order:
            self._order.append(key)

    def get_key_to_evict(self) -> K | None:
        size = len(self._order)
        if size >= self.capacity:
            return self._order[0]
        return None

    def remove_key(self, key: K) -> None:
        if key not in self._order:
            return
        self._order.remove(key)

    def clear(self) -> None:
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return len(self._order) > 0


@dataclass
class LRUPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def __init__(self, capacity: int = 5) -> None:
        self._order = []
        self.capacity = capacity

    def register_access(self, key: K) -> None:
        self.remove_key(key)
        self._order.append(key)

    def get_key_to_evict(self) -> K | None:
        size = len(self._order)
        if size >= self.capacity:
            return self._order[0]
        return None

    def remove_key(self, key: K) -> None:
        if key not in self._order:
            return
        self._order.remove(key)

    def clear(self) -> None:
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return len(self._order) > 0


@dataclass
class LFUPolicy(Policy[K]):
    capacity: int = 5
    _key_counter: dict[K, int] = field(default_factory=dict, init=False)

    def __init__(self, capacity: int = 5):
        self.capacity = capacity
        self._key_counter = {}
        self._last_key: K | None = None

    def register_access(self, key: K) -> None:
        if key not in self._key_counter:
            self._key_counter[key] = 0
        self._key_counter[key] += 1
        self._last_key = key

    def get_key_to_evict(self) -> K | None:
        size = len(self._key_counter)
        if size < self.capacity:
            return None
        key_to_del = None
        for key in self._key_counter:
            key_count = self._key_counter[key]
            key_is_none_check = key_to_del is None
            key_is_last_check = key != self._last_key
            count_check = (key_to_del is not None) and key_count < self._key_counter[key_to_del]
            if key_is_none_check or (key_is_last_check and count_check):
                key_to_del = key
        return key_to_del

    def remove_key(self, key: K) -> None:
        if key not in self._key_counter:
            return
        self._key_counter.pop(key)

    def clear(self) -> None:
        self._key_counter.clear()

    @property
    def has_keys(self) -> bool:
        return len(self._key_counter.keys()) > 0


class MIPTCache(Cache[K, V]):
    def __init__(self, storage: Storage[K, V], policy: Policy[K]) -> None:
        self.storage = storage
        self.policy = policy

    def set(self, key: K, value: V) -> None:
        key_to_del = self.policy.get_key_to_evict()
        if key_to_del is not None:
            self.policy.remove_key(key_to_del)
            self.storage.remove(key_to_del)
        self.policy.register_access(key)
        self.storage.set(key, value)

    def get(self, key: K) -> V | None:
        self.policy.register_access(key)
        if self.storage.exists(key):
            return self.storage.get(key)
        return None

    def exists(self, key: K) -> bool:
        return self.storage.exists(key)

    def remove(self, key: K) -> None:
        self.policy.remove_key(key)
        self.storage.remove(key)

    def clear(self) -> None:
        self.storage.clear()
        self.policy.clear()


class CachedProperty[V]:
    def __init__(self, func: Callable[..., V]) -> None:
        self.func = func
        self._name = self.func.__name__

    def __get__(self, instance: HasCache[Any, Any] | None, owner: type) -> V:
        if instance is None:
            return self  # type: ignore[return-value]

        if instance.cache.exists(self._name):
            return instance.cache.get(self._name)  # type: ignore[return-value]

        answer = self.func(instance)
        instance.cache.set(self._name, answer)
        return answer
