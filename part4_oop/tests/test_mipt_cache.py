from ast import TypeVar
from collections.abc import Callable
from typing import Any

import pytest

from part4_oop.hw45 import DictStorage, FIFOPolicy, LFUPolicy, LRUPolicy, MIPTCache
from part4_oop.tests.consts import TEST_FIRST_KEY, TEST_SECOND_KEY


def test_cache_with_lfu_policy(
    policy_generator: Callable[..., LFUPolicy[Any]],
    dict_storage: DictStorage[str, str],
    random_string_generator: Callable[..., str],
) -> None:
    policy: LFUPolicy[str] = policy_generator(LFUPolicy[str], capacity=2)
    cache = MIPTCache(storage=dict_storage, policy=policy)
    cache.set(TEST_FIRST_KEY, random_string_generator())
    cache.set(TEST_SECOND_KEY, random_string_generator())
    for _ in range(10):
        cache.get(TEST_FIRST_KEY)
    cache.set(f"{TEST_FIRST_KEY}_1", random_string_generator())
    assert not policy._key_counter.get(TEST_SECOND_KEY)  # noqa: SLF001
    assert not cache.exists(TEST_SECOND_KEY)


def test_cache_with_fifo_policy(
    policy_generator: Callable[..., FIFOPolicy[Any]],
    dict_storage: DictStorage[str, str],
    random_string_generator: Callable[..., str],
) -> None:
    policy: FIFOPolicy[str] = policy_generator(FIFOPolicy[str], capacity=2)
    cache = MIPTCache(storage=dict_storage, policy=policy)
    cache.set(TEST_FIRST_KEY, random_string_generator())
    cache.set(TEST_SECOND_KEY, random_string_generator())
    cache.set(f"{TEST_FIRST_KEY}_1", random_string_generator())
    assert TEST_FIRST_KEY not in policy._order  # noqa: SLF001
    assert not cache.exists(TEST_FIRST_KEY)


def test_cache_with_lru_policy(
    policy_generator: Callable[..., LRUPolicy[Any]],
    dict_storage: DictStorage[str, str],
    random_string_generator: Callable[..., str],
) -> None:
    policy: LRUPolicy[str] = policy_generator(LRUPolicy[str], capacity=2)
    cache = MIPTCache(storage=dict_storage, policy=policy)
    cache.set(TEST_FIRST_KEY, random_string_generator())
    cache.set(TEST_SECOND_KEY, random_string_generator())
    for _ in range(10):
        cache.get(TEST_FIRST_KEY)
    cache.get(TEST_SECOND_KEY)
    cache.set(f"{TEST_FIRST_KEY}_1", random_string_generator())
    assert TEST_FIRST_KEY not in policy._order  # noqa: SLF001
    assert not cache.exists(TEST_FIRST_KEY)
