from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


def build_create_document_params(  # noqa: D103
    file_name: str, file_data: bytes, metadata: dict[str, Any] | None, parent: str | None
) -> dict[str, Any]:
    metadata = metadata or {}
    files: dict[str, Any] = {
        "content": (file_name, file_data),
        "metadata": ("", json.dumps(metadata).encode("utf-8")),
    }
    if parent:
        files["parent"] = ("", parent)
    return files
