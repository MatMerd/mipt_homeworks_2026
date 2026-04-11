from collections.abc import Callable
from typing import Any

from part4_oop.hw45 import LFUPolicy
from part4_oop.tests.consts import TEST_FIRST_KEY, TEST_SECOND_KEY


def test_policy_without_calling(policy_generator: Callable[..., LFUPolicy[Any]]) -> None:
    policy: LFUPolicy[str] = policy_generator(LFUPolicy)
    assert policy.get_key_to_evict() is None


def test_policy_in_capacity_area(policy_generator: Callable[..., LFUPolicy[Any]]) -> None:
    policy: LFUPolicy[str] = policy_generator(LFUPolicy, capacity=3)
    policy.register_access(TEST_FIRST_KEY)
    policy.register_access(TEST_SECOND_KEY)
    assert policy.get_key_to_evict() is None


def test_policy_clear(policy_generator: Callable[..., LFUPolicy[Any]]) -> None:
    policy: LFUPolicy[str] = policy_generator(LFUPolicy, capacity=3)
    policy.register_access(TEST_FIRST_KEY)
    policy.register_access(TEST_SECOND_KEY)
    assert policy.has_keys
    policy.clear()
    assert not policy.has_keys


def test_policy_remove_key(policy_generator: Callable[..., LFUPolicy[Any]]) -> None:
    policy: LFUPolicy[str] = policy_generator(LFUPolicy, capacity=3)
    policy.register_access(TEST_FIRST_KEY)
    assert policy.has_keys
    policy.remove_key(TEST_FIRST_KEY)
    assert not policy.has_keys


def test_lfu_behaviour(policy_generator: Callable[..., LFUPolicy[Any]]) -> None:
    policy: LFUPolicy[str] = policy_generator(LFUPolicy, capacity=2)
    for _ in range(3):
        policy.register_access(TEST_FIRST_KEY)
    policy.register_access(TEST_SECOND_KEY)
    policy.register_access(f"{TEST_SECOND_KEY}_1")
    assert policy.get_key_to_evict() == TEST_SECOND_KEY


def test_delete_popular_key(policy_generator: Callable[..., LFUPolicy[Any]]) -> None:
    policy: LFUPolicy[str] = policy_generator(LFUPolicy)
    access_count = 10
    for _ in range(access_count):
        policy.register_access(TEST_FIRST_KEY)
    assert policy._key_counter[TEST_FIRST_KEY] == access_count  # noqa: SLF001
    policy.remove_key(TEST_FIRST_KEY)
    policy.register_access(TEST_FIRST_KEY)
    assert policy._key_counter[TEST_FIRST_KEY] == 1  # noqa: SLF001


def test_tie_break_with_equal_counter(policy_generator: Callable[..., LFUPolicy[Any]]) -> None:
    policy: LFUPolicy[str] = policy_generator(LFUPolicy, capacity=2)
    access_count = 10
    for _ in range(access_count):
        policy.register_access(TEST_FIRST_KEY)
    for _ in range(access_count):
        policy.register_access(TEST_SECOND_KEY)
    policy.register_access(f"{TEST_SECOND_KEY}_1")
    assert policy.get_key_to_evict() == TEST_FIRST_KEY
