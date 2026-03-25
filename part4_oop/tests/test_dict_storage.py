import random
import string
from typing import Any

import pytest

from part4_oop.hw45 import DictStorage
from part4_oop.tests.consts import TEST_FIRST_KEY, TEST_SECOND_KEY


def test_initial_state(dict_storage: DictStorage[str, str]) -> None:
    assert not dict_storage.exists(TEST_FIRST_KEY)
    assert dict_storage.get(TEST_FIRST_KEY) is None


def test_set_key(dict_storage: DictStorage[str, str]) -> None:
    value = random.choice(string.ascii_letters)
    dict_storage.set(TEST_FIRST_KEY, value)
    assert dict_storage._data[TEST_FIRST_KEY] == value  # noqa: SLF001
    assert dict_storage.get(TEST_FIRST_KEY) == value


def test_double_set_key(dict_storage: DictStorage[str, str]) -> None:
    dict_storage.set(TEST_FIRST_KEY, random.choice(string.ascii_letters))
    value = random.choice(string.ascii_letters)
    dict_storage.set(TEST_FIRST_KEY, value)
    assert dict_storage._data[TEST_FIRST_KEY] == value  # noqa: SLF001
    assert dict_storage.get(TEST_FIRST_KEY) == value


@pytest.mark.parametrize(
    ("key", "value"),
    [
        (1, 1),
        ("key", "value"),
        ((1,), (1,)),
        (1.0, 1.0),
        ("list", [1, 2, 3, 4]),
        ("set", {1, 2, 3, 4}),
        ("dict", {1: 1, 2: 2}),
        ("object", object()),
        (None, 1),
        ("", 1),
        ("empty", ""),
    ],
)
def test_different_key_types(key: Any, value: Any, dict_storage: DictStorage[Any, str]) -> None:
    dict_storage.set(key, value)
    assert dict_storage.get(key) == value


def test_key_exists(dict_storage: DictStorage[str, str]) -> None:
    dict_storage.set(TEST_FIRST_KEY, "1")
    assert dict_storage.exists(TEST_FIRST_KEY)


def test_key_not_exists(dict_storage: DictStorage[str, str]) -> None:
    dict_storage.set(TEST_FIRST_KEY, "1")
    assert not dict_storage.exists(TEST_SECOND_KEY)


def test_remove_key(dict_storage: DictStorage[str, str]) -> None:
    dict_storage.set(TEST_FIRST_KEY, "1")
    dict_storage.remove(TEST_FIRST_KEY)
    assert not dict_storage.exists(TEST_FIRST_KEY)
    assert dict_storage.get(TEST_FIRST_KEY) is None


def test_remove_not_exists_key(dict_storage: DictStorage[str, str]) -> None:
    dict_storage.remove(TEST_FIRST_KEY)


def test_clear(dict_storage: DictStorage[str, str]) -> None:
    for i in range(10):
        dict_storage.set(f"{TEST_FIRST_KEY}_{i}", str(i))
        assert dict_storage.exists(f"{TEST_FIRST_KEY}_{i}")
    dict_storage.clear()
    for i in range(10):
        assert not dict_storage.exists(f"{TEST_FIRST_KEY}_{i}")
