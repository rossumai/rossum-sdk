from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Hook:
    id: int
    name: str
    url: str
    active: bool
    config: Dict[str, Any]
    test: Dict[str, Any]
    guide: str | None
    read_more_url: str | None
    extension_image_url: str | None
    type: str = "webhook"
    metadata: Dict[str, Any] = field(default_factory=dict)
    queues: List[str] = field(default_factory=list)
    run_after: List[str] = field(default_factory=list)
    events: List[str] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)
    settings_schema: Dict[str, Any] | None = None
    secrets: Dict[str, Any] = field(default_factory=dict)
    extension_source: str = "custom"
    sideload: List[str] = field(default_factory=list)
    token_owner: str | None = None
    token_lifetime_s: int | None = None
    description: str | None = None
