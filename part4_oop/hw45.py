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
        return self._data.get(key)

    def exists(self, key: K) -> bool:
        return key in self._data

    def remove(self, key: K) -> None:
        self._data.pop(key, None)

    def clear(self) -> None:
        self._data.clear()


@dataclass
class FIFOPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def register_access(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)
        self._order.append(key)

    def get_key_to_evict(self) -> K | None:
        if len(self._order) > self.capacity:
            return self._order[0]
        return None

    def remove_key(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)

    def clear(self) -> None:
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return bool(self._order)


@dataclass
class LRUPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def register_access(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)
        self._order.append(key)

    def get_key_to_evict(self) -> K | None:
        if len(self._order) > self.capacity:
            return self._order[0]
        return None

    def remove_key(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)

    def clear(self) -> None:
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return bool(self._order)


@dataclass
class LFUPolicy(Policy[K]):
    capacity: int = 5
    _key_counter: dict[K, int] = field(default_factory=dict, init=False)

    def register_access(self, key: K) -> None:
        if key in self._key_counter:
            self._key_counter[key] += 1
        else:
            self._key_counter[key] = 1

    def get_key_to_evict(self) -> K | None:
        if len(self._key_counter) > self.capacity:
            return min(self._key_counter, key=self._key_counter.get)
        return None

    def remove_key(self, key: K) -> None:
        if key in self._key_counter:
            del self._key_counter[key]

    def clear(self) -> None:
        self._key_counter.clear()

    @property
    def has_keys(self) -> bool:
        return bool(self._key_counter)

    def __init__(self, capacity: int = 5) -> None:
        self.capacity = capacity
        self._key_counter = {}


class MIPTCache(Cache[K, V]):
    def __init__(self, storage: Storage[K, V], policy: Policy[K]) -> None:
        self.storage = storage
        self.policy = policy

    def set(self, key: K, value: V) -> None:
        self._policy.register_access(key)
        evict_key = self._policy.get_key_to_evict()
        if evict_key is not None:
            self._storage.remove(evict_key)
            self._policy.remove_key(evict_key)
        self._storage.set(key, value)

    def get(self, key: K) -> V | None:
        if self._storage.exists(key):
            self._policy.register_access(key)
        return self._storage.get(key)

    def exists(self, key: K) -> bool:
        return self._storage.exists(key)

    def remove(self, key: K) -> None:
        self._storage.remove(key)
        self._policy.remove_key(key)

    def clear(self) -> None:
        self._storage.clear()
        self._policy.clear()


class CachedProperty[V]:
    def __init__(self, func: Callable[..., V]) -> None:
        self._func = func
        self._cache_key = func.__name__

    def __get__(self, instance: HasCache[Any, Any] | None, owner: type) -> V:
        if instance is None:
            return self._func  # type: ignore
        # Так разрешил делать Матвей :)
        cached = instance.cache.get(self._cache_key)
        if cached is not None:
            return cached

        result = self._func(instance)
        instance.cache.set(self._cache_key, result)
        return result
