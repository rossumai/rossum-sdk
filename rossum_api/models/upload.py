from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Upload:
    """Represents https://elis.rossum.ai/api/docs/#upload."""

    id: int
    url: str
    queue: str
    organization: str
    creator: str
    created_at: str
    documents: list[str]
    additional_documents: list[str] = field(default_factory=list)
    annotations: list[str] = field(default_factory=list)
    email: str | None = None
