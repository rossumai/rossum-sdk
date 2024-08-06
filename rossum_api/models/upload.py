from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Upload:
    """Represents https://elis.rossum.ai/api/docs/#upload."""

    id: int
    url: str
    queue: str
    organization: str
    creator: str
    created_at: str
    documents: List[str]
    additional_documents: List[str] = field(default_factory=list)
    annotations: List[str] = field(default_factory=list)
    email: Optional[str] = None
