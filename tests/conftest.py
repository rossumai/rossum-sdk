from unittest.mock import MagicMock

import pytest
import pytest_asyncio

from rossum_ng.api_client import APIClient


@pytest.fixture
def http_client():
    return MagicMock(APIClient)


@pytest_asyncio.fixture
async def mock_generator():
    async def f(item):
        for org in [item]:
            yield org

    return f
