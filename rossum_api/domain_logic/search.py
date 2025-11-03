from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


def validate_search_params(query: dict | None = None, query_string: dict | None = None) -> None:  # noqa: D103
    if not query and not query_string:
        raise ValueError("Either query or query_string must be provided")


def build_search_params(  # noqa: D103
    query: dict | None = None, query_string: dict | None = None
) -> dict[str, Any]:
    json_payload = {}
    if query:
        json_payload["query"] = query
    if query_string:
        json_payload["query_string"] = query_string
    return json_payload
