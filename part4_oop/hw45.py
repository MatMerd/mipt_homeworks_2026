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
        return self._data.get(key, None)

    def exists(self, key: K) -> bool:
        return (key in self._data)

    def remove(self, key: K) -> None:
        self._data.pop(key, None)

    def clear(self) -> None:
        self._data.clear()


@dataclass
class FIFOPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)
    key_to_evict: K = None

    def register_access(self, key: K) -> None:
        if len(self._order) == self.capacity and not key in self._order:
            self.key_to_evict = self._order[0]

        if not key in self._order:
            self._order.append(key)

    def get_key_to_evict(self) -> K | None:
        if len(self._order) > self.capacity:
            return self.key_to_evict
        
    def remove_key(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)

    def clear(self) -> None:
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return (len(self._order) > 0)


@dataclass
class LRUPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)
    key_to_evict: K = None

    def register_access(self, key: K) -> None:
        if len(self._order) == self.capacity and not key in self._order:
            self.key_to_evict = self._order[0]

        if key in self._order:
            self._order.remove(key)
        self._order.append(key)

    def get_key_to_evict(self) -> K | None:
        if len(self._order) > self.capacity:
            return self.key_to_evict
        
    def remove_key(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)

    def clear(self) -> None:
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return (len(self._order) > 0)


@dataclass
class LFUPolicy(Policy[K]):
    capacity: int = 5
    _key_counter: dict[K, int] = field(default_factory=dict, init=False)
    key_to_evict: K = None

    def register_access(self, key: K) -> None:
        if len(self._key_counter) == self.capacity and not key in self._key_counter:
            least_frequently_used = next(iter(self._key_counter))
            for real_key in self._key_counter:
                if self._key_counter[real_key] < self._key_counter[least_frequently_used]:
                    least_frequently_used = real_key
            self.key_to_evict = least_frequently_used
        
        if not key in self._key_counter:
            self._key_counter[key] = 0
        self._key_counter[key] += 1

    def get_key_to_evict(self) -> K | None:
        if len(self._key_counter) > self.capacity:
            return self.key_to_evict
        
    def remove_key(self, key: K) -> None:
        self._key_counter.pop(key, None)

    def clear(self) -> None:
        self._key_counter.clear()

    @property
    def has_keys(self) -> bool:
        return (len(self._key_counter) > 0)


class MIPTCache(Cache[K, V]):
    def __init__(self, storage: Storage[K, V], policy: Policy[K]) -> None:
        self.storage = storage
        self.policy = policy

    def set(self, key: K, value: V) -> None:
        self.storage.set(key, value)
        self.policy.register_access(key)

        key_to_evict = self.policy.get_key_to_evict()
        if not key_to_evict is None:
            self.remove(key_to_evict)

    def get(self, key: K) -> V | None:
        if not self.storage.exists(key):
            return None
        self.policy.register_access(key)
        return self.storage.get(key)

    def exists(self, key: K) -> bool:
        return self.storage.exists(key)

    def remove(self, key: K) -> None:
        self.storage.remove(key)
        self.policy.remove_key(key)

    def clear(self) -> None:
        self.storage.clear()
        self.policy.clear()


class CachedProperty[V]:
    def __init__(self, func: Callable[..., V]) -> None:
        self._func = func
        self._key = func.__repr__

    def __get__(self, instance: HasCache[Any, Any] | None, owner: type) -> V | None:
        if instance is None:
            return None

        if not instance.cache.exists(self._key):
            instance.cache.set(self._key, self._func(instance))
        return instance.cache.get(self._key)