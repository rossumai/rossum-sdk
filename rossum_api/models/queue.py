from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


@dataclass
class Queue:
    id: int
    name: str
    url: str
    workspace: Optional[str]
    connector: Optional[str]
    schema: str
    inbox: Optional[str]
    counts: Dict[str, int]
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
    metadata: Dict[str, Any] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)
    dedicated_engine: Optional[Union[str, Dict[str, Any]]] = None
    generic_engine: Optional[Union[str, Dict[str, Any]]] = None
    use_confirmed_state: bool = False
    document_lifetime: Optional[str] = None
    delete_after: Optional[str] = None
    status: Optional[str] = None
    engine: Optional[str] = None
    training_enabled: bool = True
