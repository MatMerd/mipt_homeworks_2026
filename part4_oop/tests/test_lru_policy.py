from collections.abc import Callable
from typing import Any

from part4_oop.hw45 import LRUPolicy
from part4_oop.tests.consts import TEST_FIRST_KEY, TEST_SECOND_KEY


def test_policy_without_calling(policy_generator: Callable[..., LRUPolicy[Any]]) -> None:
    policy: LRUPolicy[str] = policy_generator(LRUPolicy)
    assert policy.get_key_to_evict() is None


def test_policy_in_capacity_area(policy_generator: Callable[..., LRUPolicy[Any]]) -> None:
    policy: LRUPolicy[str] = policy_generator(LRUPolicy, capacity=3)
    policy.register_access(TEST_FIRST_KEY)
    policy.register_access(TEST_SECOND_KEY)
    assert policy.get_key_to_evict() is None


def test_policy_clear(policy_generator: Callable[..., LRUPolicy[Any]]) -> None:
    policy: LRUPolicy[str] = policy_generator(LRUPolicy, capacity=3)
    policy.register_access(TEST_FIRST_KEY)
    policy.register_access(TEST_SECOND_KEY)
    assert policy.has_keys
    policy.clear()
    assert not policy.has_keys


def test_policy_remove_key(policy_generator: Callable[..., LRUPolicy[Any]]) -> None:
    policy: LRUPolicy[str] = policy_generator(LRUPolicy, capacity=3)
    policy.register_access(TEST_FIRST_KEY)
    assert policy.has_keys
    policy.remove_key(TEST_FIRST_KEY)
    assert not policy.has_keys


def test_lru_behaviour(policy_generator: Callable[..., LRUPolicy[Any]]) -> None:
    policy: LRUPolicy[str] = policy_generator(LRUPolicy, capacity=2)
    policy.register_access(TEST_FIRST_KEY)
    policy.register_access(TEST_SECOND_KEY)
    policy.register_access(TEST_FIRST_KEY)
    policy.register_access(f"{TEST_SECOND_KEY}_2")
    assert policy.get_key_to_evict() == TEST_SECOND_KEY


def test_multiple_register_one_key(policy_generator: Callable[..., LRUPolicy[Any]]) -> None:
    policy: LRUPolicy[str] = policy_generator(LRUPolicy, capacity=20)
    access_count = 5
    for _ in range(access_count):
        policy.register_access(TEST_FIRST_KEY)
    assert TEST_FIRST_KEY in policy._order  # noqa: SLF001
    assert policy._order[-1] == TEST_FIRST_KEY  # noqa: SLF001
    policy.register_access(TEST_SECOND_KEY)
    policy.register_access(TEST_FIRST_KEY)
    assert TEST_FIRST_KEY in policy._order  # noqa: SLF001
    assert policy._order[-1] == TEST_FIRST_KEY  # noqa: SLF001
