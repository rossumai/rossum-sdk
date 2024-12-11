from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Optional


def build_upload_files(
    file_content: bytes,
    filename: str,
    values: Optional[dict[str, Any]] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Build request files for the upload endpoint."""
    files = {"content": (filename, file_content, "application/octet-stream")}

    # Filename of values and metadata must be "", otherwise Elis API returns HTTP 400 with body
    # "Value must be valid JSON."
    if values is not None:
        files["values"] = ("", json.dumps(values).encode("utf-8"), "application/json")
    if metadata is not None:
        files["metadata"] = ("", json.dumps(metadata).encode("utf-8"), "application/json")

    return files
