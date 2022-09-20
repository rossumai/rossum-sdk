from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Schema:
    id: int
    name: Optional[str] = None
    queues: List[str] = field(default_factory=list)
    url: Optional[str] = None
    content: List[Dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
