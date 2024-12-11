from __future__ import annotations

import json
from typing import Any, Optional

import httpx


def build_create_document_params(
    file_name: str,
    file_data: bytes,
    metadata: Optional[dict[str, Any]],
    parent: Optional[str],
) -> dict[str, Any]:
    metadata = metadata or {}
    files: httpx._types.RequestFiles = {
        "content": (file_name, file_data),
        "metadata": ("", json.dumps(metadata).encode("utf-8")),
    }
    if parent:
        files["parent"] = ("", parent)
    return files
