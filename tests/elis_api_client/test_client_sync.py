from __future__ import annotations

import httpx
import pytest


class TestClientSync:
    def test_request_paginated(self, elis_client_sync, mock_generator):
        client, http_client = elis_client_sync
        http_client.fetch_all_by_url.return_value = mock_generator({"some": "json"})
        kwargs = {"whatever": "kwarg"}
        data = client.request_paginated("hook_templates", **kwargs)
        assert list(data) == [{"some": "json"}]

    def test_request_paginated_propagates_errors(self, elis_client_sync):
        client, http_client = elis_client_sync
        http_client.fetch_all_by_url.side_effect = Exception("Exception in async code.")
        with pytest.raises(Exception, match="Exception in async code."):
            list(client.request_paginated("hook_templates"))

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
