import aiofiles
import pytest
import pytest_asyncio
from mock import MagicMock

from rossum_ng.api_client import APIClient
from rossum_ng.elis_api_client import ElisAPIClient
from rossum_ng.elis_api_client_sync import ElisAPIClientSync


@pytest.fixture
def http_client():
    return MagicMock(APIClient)


@pytest_asyncio.fixture
def elis_client(http_client):
    client = ElisAPIClient(username="", password="", base_url=None, http_client=http_client)
    return (client, http_client)


@pytest.fixture
def elis_client_sync(http_client):
    client = ElisAPIClientSync(username="", password="", base_url=None, http_client=http_client)
    return (client, http_client)


@pytest_asyncio.fixture
async def mock_generator():
    async def f(item):
        for i in [item]:
            yield i

    return f


@pytest_asyncio.fixture
async def mock_file_read():
    async def f(path):
        async with aiofiles.open(path, "rb") as fp:
            async for line in fp:
                yield line

    return f
