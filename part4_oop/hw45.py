from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

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
    _order: list[K] = field(default_factory=list, init=False)
    _pending: K | None = field(default=None, init=False)

    def register_access(self, key: K) -> None:
        if key in self._key_counter:
            cnt = self._key_counter.get(key, 0) + 1
            self._key_counter.update({key: cnt})
        elif len(self._key_counter) < self.capacity:
            self._key_counter.setdefault(key, 1)
            self._order.append(key)
        else:
            self._pending = key

    def get_key_to_evict(self) -> K | None:
        total = len(self._key_counter)
        if self._pending is not None:
            total += 1
        if total <= self.capacity:
            return None
        min_cnt = min(self._key_counter.values())
        for k in self._order:
            if self._key_counter[k] == min_cnt:
                return k
        return None

    def remove_key(self, key: K) -> None:
        if key in self._key_counter:
            self._key_counter.pop(key)
            if key in self._order:
                self._order.remove(key)
        if self._pending is not None:
            p = self._pending
            self._pending = None
            self._key_counter.setdefault(p, 1)
            self._order.append(p)

    def clear(self) -> None:
        self._key_counter.clear()
        self._order.clear()
        self._pending = None

    @property
    def has_keys(self) -> bool:
        return bool(self._key_counter)


class MIPTCache(Cache[K, V]):
    def __init__(self, storage: Storage[K, V], policy: Policy[K]) -> None:
        self.storage = storage
        self.policy = policy

    def set(self, key: K, value: V) -> None:
        self.policy.register_access(key)
        to_evict = self.policy.get_key_to_evict()
        if to_evict is not None:
            self.storage.remove(to_evict)
            self.policy.remove_key(to_evict)
        self.storage.set(key, value)

    def get(self, key: K) -> V | None:
        val = self.storage.get(key)
        if val is not None:
            self.policy.register_access(key)
        return val

    def exists(self, key: K) -> bool:
        return self.storage.exists(key)

    def remove(self, key: K) -> None:
        self.storage.remove(key)
        self.policy.remove_key(key)

    def clear(self) -> None:
        self.storage.clear()
        self.policy.clear()


class CachedProperty:
    def __init__(self, func: Callable[..., Any]) -> None:
        self.func = func
        self.attr_name: str | None = None

    def __set_name__(self, owner: type, name: str) -> None:
        self.attr_name = name

    def __get__(self, instance: HasCache[Any, Any] | None, owner: type) -> Any:
        if instance is None:
            return self
        val = instance.cache.get(self.attr_name)
        if val is not None:
            return val
        val = self.func(instance)
        instance.cache.set(self.attr_name, val)
        return val
