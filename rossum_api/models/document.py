from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Document:
    id: int
    url: str
    s3_name: str
    parent: str | None
    email: str | None
    mime_type: str
    creator: str | None
    created_at: str
    arrived_at: str
    original_file_name: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    annotations: List[str] = field(default_factory=list)
    attachment_status: str | None = None
