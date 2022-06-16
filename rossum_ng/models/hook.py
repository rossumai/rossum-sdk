from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional


@dataclass
class Hook:
    id: int
    name: str
    url: str
    active: bool
    config: dict[str, Any]
    test: dict[str, Any]
    guide: str
    read_more_url: str
    extension_image_url: str
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
    description: Optional[str] = None
