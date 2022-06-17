from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Queue:
    id: int
    name: str
    url: str
    workspace: str
    connector: Optional[str]
    schema: str
    inbox: Optional[str]
    counts: Dict[str, str]
    session_timeout: str = "01:00:00"
    webhooks: List[str] = field(default_factory=list)
    hooks: List[str] = field(default_factory=list)
    users: List[str] = field(default_factory=list)
    rir_url: Optional[str] = None
    rir_params: Optional[str] = None
    automation_enabled: bool = False
    automation_level: str = "never"
    default_score_threshold: float = 0.8
    locale: str = "en_GB"
    metadata: Dict[str, str] = field(default_factory=dict)
    settings: Dict[str, str] = field(default_factory=dict)
    dedicated_engine: Optional[Dict[str, str]] = None
    generic_engine: Optional[Dict[str, str]] = None
    use_confirmed_state: bool = False
    document_lifetime: Optional[int] = None
