from __future__ import annotations

from typing import Any, Optional


def validate_search_params(
    query: Optional[dict] = None,
    query_string: Optional[dict] = None,
):
    if not query and not query_string:
        raise ValueError("Either query or query_string must be provided")


def build_search_params(
    query: Optional[dict] = None,
    query_string: Optional[dict] = None,
) -> dict[str, Any]:
    json_payload = {}
    if query:
        json_payload["query"] = query
    if query_string:
        json_payload["query_string"] = query_string
    return json_payload
