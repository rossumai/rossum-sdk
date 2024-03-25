from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AutomationBlockerContent:
    level: str
    type: str
    schema_id: Optional[str] = None
    samples_truncated: Optional[bool] = False
    samples: List[Dict[str, Any]] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AutomationBlocker:
    id: int
    url: str
    annotation: str
    content: List[AutomationBlockerContent] = field(default_factory=list)
