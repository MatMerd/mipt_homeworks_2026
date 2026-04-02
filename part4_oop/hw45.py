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
    _recent_key: K | None = field(default=None, init=False)
    _recent_is_new: bool = field(default=False, init=False)

    def register_access(self, key: K) -> None:
        self._recent_is_new = key not in self._order
        self._recent_key = key
        if key not in self._order:
            self._order.append(key)

    def get_key_to_evict(self) -> K | None:
        if not self._order or not self._recent_is_new:
            return None

        if len(self._order) < self.capacity:
            return None

        if self._recent_key is None:
            return self._order[0]

        for key in self._order:
            if key != self._recent_key:
                return key
        return None

    def remove_key(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)
        if key == self._recent_key:
            self._recent_key = None
            self._recent_is_new = False

    def clear(self) -> None:
        self._order.clear()
        self._recent_key = None
        self._recent_is_new = False

    @property
    def has_keys(self) -> bool:
        return bool(self._order)


@dataclass
class LRUPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)
    _recent_key: K | None = field(default=None, init=False)
    _recent_is_new: bool = field(default=False, init=False)

    def register_access(self, key: K) -> None:
        self._recent_is_new = key not in self._order
        self._recent_key = key
        if key in self._order:
            self._order.remove(key)
        self._order.append(key)

    def get_key_to_evict(self) -> K | None:
        if not self._order or not self._recent_is_new:
            return None

        if len(self._order) < self.capacity:
            return None

        if self._recent_key is None:
            return self._order[0]

        for key in self._order:
            if key != self._recent_key:
                return key
        return None

    def remove_key(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)
        if key == self._recent_key:
            self._recent_key = None
            self._recent_is_new = False

    def clear(self) -> None:
        self._order.clear()
        self._recent_key = None
        self._recent_is_new = False

    @property
    def has_keys(self) -> bool:
        return bool(self._order)


@dataclass
class LFUPolicy(Policy[K]):
    capacity: int = 5
    _key_counter: dict[K, int] = field(default_factory=dict, init=False)
    _recent_key: K | None = field(default=None, init=False)
    _recent_is_new: bool = field(default=False, init=False)

    def register_access(self, key: K) -> None:
        self._recent_is_new = key not in self._key_counter
        self._recent_key = key
        self._key_counter[key] = self._key_counter.get(key, 0) + 1

    def get_key_to_evict(self) -> K | None:
        if not self._key_counter or not self._recent_is_new:
            return None

        if len(self._key_counter) < self.capacity:
            return None

        candidates = self._key_counter
        if self._recent_key is not None:
            candidates = {
                key: count
                for key, count in self._key_counter.items()
                if key != self._recent_key
            }

        if not candidates:
            return None

        min_count = min(candidates.values())
        for key, cnt in candidates.items():
            if cnt == min_count:
                return key
        return None

    def remove_key(self, key: K) -> None:
        self._key_counter.pop(key, None)
        if key == self._recent_key:
            self._recent_key = None
            self._recent_is_new = False

    def clear(self) -> None:
        self._key_counter.clear()
        self._recent_key = None
        self._recent_is_new = False

    @property
    def has_keys(self) -> bool:
        return bool(self._key_counter)


class MIPTCache(Cache[K, V]):
    def __init__(self, storage: Storage[K, V], policy: Policy[K]) -> None:
        self.storage = storage
        self.policy = policy

    def set(self, key: K, value: V) -> None:
        already_exists = self.storage.exists(key)
        self.policy.register_access(key)

        if not already_exists:
            capacity = getattr(self.policy, "capacity", None)
            storage_size = self._storage_size()
            if (
                isinstance(capacity, int)
                and isinstance(storage_size, int)
                and storage_size >= capacity
            ):
                evict = self.policy.get_key_to_evict()
                if evict is not None and self.storage.exists(evict):
                    self.storage.remove(evict)
                    self.policy.remove_key(evict)

        self.storage.set(key, value)

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

    def _storage_size(self) -> int | None:
        data = getattr(self.storage, "_data", None)
        if isinstance(data, dict):
            return len(data)
        return None


class CachedProperty[V]:
    def __init__(self, func: Callable[..., V]) -> None:
        self._func = func
        self._name = func.__name__

    def __get__(self, instance: HasCache[Any, Any] | None, owner: type[Any]) -> Any:
        if instance is None:
            return self

        cache: Cache[Any, Any] = instance.cache
        key = (owner, self._name)

        if cache.exists(key):
            return cache.get(key)

        value = self._func(instance)
        cache.set(key, value)
        return value
