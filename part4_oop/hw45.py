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
        if key not in self._order:
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
    _pending_evict_key: K | None = field(default=None, init=False)

    def register_access(self, key: K) -> None:
        if key in self._key_counter:
            cur_counter = self._key_counter.get(key, 0)
            self._key_counter.update({key: cur_counter + 1})
            return
        self._pending_evict_key = None
        if len(self._key_counter) >= self.capacity and self._key_counter:
            self._pending_evict_key = min(
                self._key_counter.items(),
                key=lambda item: item[1],
            )[0]
        self._key_counter[key] = 1

    def get_key_to_evict(self) -> K | None:
        if len(self._key_counter) <= self.capacity:
            return None
        if self._pending_evict_key is not None:
            return self._pending_evict_key
        return min(
            self._key_counter.items(),
            key=lambda item: item[1],
        )[0]

    def remove_key(self, key: K) -> None:
        self._key_counter.pop(key, None)
        if self._pending_evict_key == key:
            self._pending_evict_key = None

    def clear(self) -> None:
        self._key_counter.clear()
        self._pending_evict_key = None

    @property
    def has_keys(self) -> bool:
        return bool(self._key_counter)


class MIPTCache(Cache[K, V]):
    def __init__(self, storage: Storage[K, V], policy: Policy[K]) -> None:
        self.storage = storage
        self.policy = policy

    def set(self, key: K, value: V) -> None:
        self.storage.set(key, value)
        self.policy.register_access(key)
        key_to_evict = self.policy.get_key_to_evict()
        if key_to_evict is None:
            return
        self.storage.remove(key_to_evict)
        self.policy.remove_key(key_to_evict)

    def get(self, key: K) -> V | None:
        value = self.storage.get(key)
        if value is None:
            return None
        self.policy.register_access(key)
        return value

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

    def __set_name__(self, owner: type, name: str) -> None:
        self._cache_key = name

    def __get__(self, instance: HasCache[Any, V] | None, owner: type) -> V:
        if instance is None:
            return self  # type: ignore[return-value]
        cached_value = instance.cache.get(self._cache_key)
        if cached_value is not None:
            return cached_value
        value = self._func(instance)
        instance.cache.set(self._cache_key, value)
        return value

