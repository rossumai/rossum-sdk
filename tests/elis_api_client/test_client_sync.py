import pytest
from mock import patch
from mock.mock import MagicMock

from rossum_ng.elis_api_client_sync import AsyncRuntimeError, ElisAPIClientSync


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
