from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Schema:
    id: int
    name: Optional[str] = None
    queues: List[str] = field(default_factory=list)
    url: Optional[str] = None
    content: List[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
