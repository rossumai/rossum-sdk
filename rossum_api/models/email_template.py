from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


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
    triggers: list[str] = field(default_factory=list)
    to: list[dict[str, Any]] = field(default_factory=list)
    cc: list[dict[str, Any]] = field(default_factory=list)
    bcc: list[dict[str, Any]] = field(default_factory=list)
