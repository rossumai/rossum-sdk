import pytest

from rossum_ng.api_client import APIClient
from unittest.mock import MagicMock


@pytest.fixture
def http_client():
    return MagicMock(APIClient)
