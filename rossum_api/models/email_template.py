from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class EmailTemplate:
    id: int
    name: str
    url: str
    queue: str
    organization: str
    subject: str
    message: str
    type: str
    enabled: bool
    automate: bool
    triggers: List[str] = field(default_factory=list)
    to: List[Dict[str, Any]] = field(default_factory=list)
    cc: List[Dict[str, Any]] = field(default_factory=list)
    bcc: List[Dict[str, Any]] = field(default_factory=list)
