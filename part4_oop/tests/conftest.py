from collections.abc import Callable
from typing import Any

import pytest

from part4_oop.hw45 import DictStorage
from part4_oop.interfaces import Policy


@pytest.fixture
def policy_generator() -> Callable[..., Policy[Any]]:
    def generator(policy: type[Policy[Any]], **policy_settings: Any) -> Policy[Any]:
        return policy(**policy_settings)

    return generator


@pytest.fixture
def dict_storage() -> DictStorage[str, str]:
    return DictStorage()
