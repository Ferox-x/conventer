import pytest

from tests.utils import AppTestClient


@pytest.fixture
def api():
    return AppTestClient()
