from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

from interfaces import Cache, HasCache, Policy, Storage

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class DictStorage(Storage[K, V]):
    _data: dict[K, V] = field(default_factory=dict, init=False)

    def set(self, key: K, value: V) -> None:
        self._data[key] = value

    def get(self, key: K) -> V | None:
        if (key in self._data):
            return self._data[key]
        return None

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
        if (key not in self._order):
            self._order.append(key)

    def get_key_to_evict(self) -> K | None:
        if (len(self._order) > self.capacity):
            return self._order[0]
        return None

    def remove_key(self, key: K) -> None:
        self._order.remove(key)

    def clear(self) -> None:
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return len(self._order) != 0


@dataclass
class LRUPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def register_access(self, key: K) -> None:
        if (key in self._order):
            self._order.remove(key)
        self._order.append(key)

    def get_key_to_evict(self) -> K | None:
        if (len(self._order) > self.capacity):
            return self._order[0]
        return None

    def remove_key(self, key: K) -> None:
        self._order.remove(key)

    def clear(self) -> None:
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return len(self._order) != 0


@dataclass
class LFUPolicy(Policy[K]):
    capacity: int = 5
    _key_counter: dict[K, int] = field(default_factory=dict, init=False)

    def register_access(self, key: K) -> None:
        if (key in self._key_counter):
            self._key_counter[key] += 1
            return
        self._key_counter[key] = 1

    def get_key_to_evict(self) -> K | None:
        if (len(self._key_counter) > self.capacity):
            return min(self._key_counter, key=lambda k: self._key_counter[k])
        return None

    def remove_key(self, key: K) -> None:
        self._key_counter.pop(key)

    def clear(self) -> None:
        self._key_counter.clear()

    @property
    def has_keys(self) -> bool:
        return len(self._key_counter) != 0


class MIPTCache(Cache[K, V]):
    def __init__(self, storage: Storage[K, V], policy: Policy[K]) -> None:
        self.storage = storage
        self.policy = policy

    def set(self, key: K, value: V) -> None:
        self.policy.register_access(key)
        result = self.policy.get_key_to_evict()

        if (result is not None):
            self.policy.remove_key(result)
            self.storage.remove(result)
        self.storage.set(key, value)

    def get(self, key: K) -> V | None:
        if (self.storage.exists(key)):
            self.policy.register_access(key)
        return self.storage.get(key)

    def exists(self, key: K) -> bool:
        return self.storage.exists(key)

    def remove(self, key: K) -> None:
        if (self.storage.exists(key)):
            self.policy.remove_key(key)
            self.storage.remove(key)

    def clear(self) -> None:
        self.policy.clear()
        self.storage.clear()


class CachedProperty[V]:
    def __init__(self, func: Callable[..., V]) -> None:
        self.func = func
        self.name = func.__name__

    def __get__(self, instance: HasCache[Any, Any] | None, owner: type) -> V | None:
        if instance is None:
            return None
        if (instance.cache.exists(self.name)):
            return instance.cache.get(self.name)
        value = self.func(instance)
        instance.cache.set(self.name, value)
        return value
