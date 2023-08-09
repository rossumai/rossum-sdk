from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Hook:
    id: int
    name: str
    url: str
    active: bool
    config: Dict[str, Any]
    test: Dict[str, Any]
    guide: Optional[str]
    read_more_url: Optional[str]
    extension_image_url: Optional[str]
    type: str = "webhook"
    metadata: Dict[str, Any] = field(default_factory=dict)
    queues: List[str] = field(default_factory=list)
    run_after: List[str] = field(default_factory=list)
    events: List[str] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)
    settings_schema: Optional[Dict[str, Any]] = None
    secrets: Dict[str, Any] = field(default_factory=dict)
    extension_source: str = "custom"
    sideload: List[str] = field(default_factory=list)
    token_owner: Optional[str] = None
    token_lifetime_s: Optional[int] = None
    description: Optional[str] = None
