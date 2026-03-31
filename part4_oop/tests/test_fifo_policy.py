from collections.abc import Callable
from typing import Any

from part4_oop.hw45 import FIFOPolicy
from part4_oop.tests.consts import TEST_FIRST_KEY, TEST_SECOND_KEY


def test_policy_without_calling(policy_generator: Callable[..., FIFOPolicy[Any]]) -> None:
    policy: FIFOPolicy[str] = policy_generator(FIFOPolicy)
    assert policy.get_key_to_evict() is None


def test_policy_in_capacity_area(policy_generator: Callable[..., FIFOPolicy[Any]]) -> None:
    policy: FIFOPolicy[str] = policy_generator(FIFOPolicy, capacity=3)
    policy.register_access(TEST_FIRST_KEY)
    policy.register_access(TEST_SECOND_KEY)
    assert policy.get_key_to_evict() is None


def test_policy_clear(policy_generator: Callable[..., FIFOPolicy[Any]]) -> None:
    policy: FIFOPolicy[str] = policy_generator(FIFOPolicy, capacity=3)
    policy.register_access(TEST_FIRST_KEY)
    policy.register_access(TEST_SECOND_KEY)
    assert policy.has_keys
    policy.clear()
    assert not policy.has_keys


def test_policy_remove_key(policy_generator: Callable[..., FIFOPolicy[Any]]) -> None:
    policy: FIFOPolicy[str] = policy_generator(FIFOPolicy, capacity=3)
    policy.register_access(TEST_FIRST_KEY)
    assert policy.has_keys
    policy.remove_key(TEST_FIRST_KEY)
    assert not policy.has_keys


def test_fifo_behaviour(policy_generator: Callable[..., FIFOPolicy[Any]]) -> None:
    policy: FIFOPolicy[str] = policy_generator(FIFOPolicy, capacity=2)
    policy.register_access(TEST_FIRST_KEY)
    policy.register_access(TEST_SECOND_KEY)
    policy.register_access(f"{TEST_FIRST_KEY}_1")
    assert policy.get_key_to_evict() == TEST_FIRST_KEY


def test_ignore_secondary_register(policy_generator: Callable[..., FIFOPolicy[Any]]) -> None:
    policy: FIFOPolicy[str] = policy_generator(FIFOPolicy, capacity=2)
    policy.register_access(TEST_FIRST_KEY)
    policy.register_access(TEST_SECOND_KEY)
    policy.register_access(TEST_FIRST_KEY)
    policy.register_access(f"{TEST_FIRST_KEY}_1")
    assert policy.get_key_to_evict() == TEST_FIRST_KEY
