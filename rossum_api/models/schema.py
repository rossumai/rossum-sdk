from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Schema:
    id: int
    name: str | None = None
    queues: List[str] = field(default_factory=list)
    url: str | None = None
    content: List[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
