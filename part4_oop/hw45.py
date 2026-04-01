from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar, cast

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
        return key in self._data

    def remove(self, key: K) -> None:
        if self.exists(key):
            del self._data[key]

    def clear(self) -> None:
        self._data.clear()


@dataclass
class FIFOPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)
    _last_added: K | None = field(default=None, init=False)

    def register_access(self, key: K) -> None:
        if key not in self._order:
            self._order.append(key)
            self._last_added = key

    def get_key_to_evict(self) -> K | None:
        if len(self._order) <= self.capacity:
            return None

        for key in self._order:
            if key != self._last_added:
                return key
        return None

    def remove_key(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)
            if self._last_added == key:
                self._last_added = None

    def clear(self) -> None:
        self._order.clear()
        self._last_added = None

    @property
    def has_keys(self) -> bool:
        return len(self._order) > 0


@dataclass
class LRUPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)
    _last_added: K | None = field(default=None, init=False)

    def register_access(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)
        self._order.append(key)
        self._last_added = key

    def get_key_to_evict(self) -> K | None:
        if len(self._order) <= self.capacity:
            return None

        for key in self._order:
            if key != self._last_added:
                return key
        return None

    def remove_key(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)
            if self._last_added == key:
                self._last_added = None

    def clear(self) -> None:
        self._order.clear()
        self._last_added = None

    @property
    def has_keys(self) -> bool:
        return len(self._order) > 0


@dataclass
class LFUPolicy(Policy[K]):
    capacity: int = 5
    _key_counter: dict[K, int] = field(default_factory=dict, init=False)
    _key_order: dict[K, int] = field(default_factory=dict, init=False)
    _order_counter: int = field(default=0, init=False)

    def register_access(self, key: K) -> None:
        if key not in self._key_counter:
            self._key_order[key] = self._order_counter
            self._order_counter += 1
        self._key_counter[key] = self._key_counter.get(key, 0) + 1

    def get_key_to_evict(self) -> K | None:
        if len(self._key_counter) <= self.capacity:
            return None

        last_item = max(self._key_order.items(), key=lambda x: x[1])
        last_key = last_item[0]
        all_to_evict = self._key_counter.copy()
        all_to_evict.pop(last_key)
        min_freq = min(all_to_evict.values())

        old_keys = [k for k, v in all_to_evict.items() if v == min_freq]
        return min(old_keys, key=lambda k: self._key_order[k])

    def remove_key(self, key: K) -> None:
        self._key_counter.pop(key, None)
        self._key_order.pop(key, None)

    def clear(self) -> None:
        self._key_counter.clear()
        self._key_order.clear()
        self._order_counter = 0

    @property
    def has_keys(self) -> bool:
        return len(self._key_counter) > 0


class MIPTCache(Cache[K, V]):
    def __init__(self, storage: Storage[K, V], policy: Policy[K]) -> None:
        self.storage = storage
        self.policy = policy

    def set(self, key: K, value: V) -> None:
        self.policy.register_access(key)
        self.storage.set(key, value)
        self._evict_if_needed()

    def get(self, key: K) -> V | None:
        if not self.storage.exists(key):
            return None
        self.policy.register_access(key)
        return self.storage.get(key)

    def exists(self, key: K) -> bool:
        return self.storage.exists(key)

    def remove(self, key: K) -> None:
        if self.storage.exists(key):
            self.storage.remove(key)
            self.policy.remove_key(key)

    def clear(self) -> None:
        self.storage.clear()
        self.policy.clear()

    def _evict_if_needed(self) -> None:
        key_to_evict = self.policy.get_key_to_evict()
        if key_to_evict is not None:
            self.storage.remove(key_to_evict)
            self.policy.remove_key(key_to_evict)


class CachedProperty[V]:
    def __init__(self, func: Callable[..., V]) -> None:
        self.func = func
        self.name = func.__name__

    def __get__(self, instance: HasCache[Any, Any] | None, owner: type) -> V:
        if instance is None:
            return cast("V", self)

        cache = instance.cache
        key = self.name

        if cache.exists(key):
            result = cache.get(key)
            if result is not None:
                return cast("V", result)

        value = self.func(instance)
        cache.set(key, value)
        return value
