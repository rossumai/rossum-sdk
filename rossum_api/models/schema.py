from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Schema:
    id: int
    name: str | None = None
    queues: list[str] = field(default_factory=list)
    url: str | None = None
    content: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
