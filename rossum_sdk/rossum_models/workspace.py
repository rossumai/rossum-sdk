from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Workspace:
    id: int
    name: str
    url: str
    autopilot: bool
    organization: str
    queues: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
