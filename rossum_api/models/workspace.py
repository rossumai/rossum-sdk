from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Workspace:
    id: int
    name: str
    url: str
    autopilot: bool
    organization: str
    queues: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
