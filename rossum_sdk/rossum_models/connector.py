from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Connector:
    id: int
    name: str
    url: str
    service_url: str
    params: str
    client_ssl_certificate: str
    authorization_token: str
    client_ssl_key: Optional[str] = None
    queues: List[str] = field(default_factory=list)
    authorization_type: str = "secret_key"
    asynchronous: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
