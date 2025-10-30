from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AutomationBlockerContent:
    level: str
    type: str
    schema_id: str | None = None
    samples_truncated: bool | None = False
    samples: list[dict[str, Any]] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class AutomationBlocker:
    id: int
    url: str
    annotation: str
    content: list[AutomationBlockerContent] = field(default_factory=list)
