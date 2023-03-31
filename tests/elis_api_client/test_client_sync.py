from __future__ import annotations

import httpx
import pytest
from mock import patch
from mock.mock import MagicMock

from rossum_api.elis_api_client_sync import AsyncRuntimeError, ElisAPIClientSync


class TestClientSync:
    def test_new_event_loop(self):
        with patch("asyncio.get_running_loop", side_effect=RuntimeError()), patch(
            "asyncio.new_event_loop"
        ) as new_event_loop_mock:
            ElisAPIClientSync("", "", None)
            assert new_event_loop_mock.called

    def test_existing_event_loop_not_running(self):
        event_loop = MagicMock()
        event_loop.is_running = MagicMock(return_value=False)
        with patch("asyncio.get_running_loop", return_value=event_loop), patch(
            "asyncio.new_event_loop"
        ) as new_event_loop_mock:
            ElisAPIClientSync("", "", None)
            assert not new_event_loop_mock.called

    def test_existing_event_loop_running(self):
        event_loop = MagicMock()
        event_loop.is_running = MagicMock(return_value=True)
        with patch("asyncio.get_running_loop", return_value=event_loop), patch(
            "asyncio.new_event_loop"
        ) as new_event_loop_mock:
            with pytest.raises(AsyncRuntimeError):
                ElisAPIClientSync("", "", None)

            assert not new_event_loop_mock.called

    def test_request_json(self, elis_client_sync):
        client, http_client = elis_client_sync
        http_client.request_json.return_value = {"some": "json"}
        args = ["some/non/standard/url"]
        kwargs = {"whatever": "kwarg"}
        data = client.request_json("GET", *args, **kwargs)
        assert data == {"some": "json"}
        http_client.request_json.assert_called_with("GET", *args, **kwargs)

    def test_request(self, elis_client_sync):
        client, http_client = elis_client_sync
        http_client.request.return_value = httpx.Response(200, content=b"some content")
        args = ["some/non/standard/url"]
        kwargs = {"whatever": "kwarg"}
        data = client.request("GET", *args, **kwargs)
        assert data.content == b"some content"
        http_client.request.assert_called_with("GET", *args, **kwargs)
