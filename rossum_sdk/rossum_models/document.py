from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Document:
    id: int
    url: str
    s3_name: str
    parent: Optional[str]
    email: Optional[str]
    mime_type: str
    creator: Optional[str]
    created_at: str
    arrived_at: str
    original_file_name: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    annotations: List[str] = field(default_factory=list)
    attachment_status: Optional[str] = None
