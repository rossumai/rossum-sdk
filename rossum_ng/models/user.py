from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class User:
    id: int
    url: str
    first_name: str
    last_name: str
    email: str
    date_joined: str
    username: str
    organization: str
    last_login: str
    is_active: bool = True
    password: Optional[str] = None
    groups: List[str] = field(default_factory=list)
    queues: List[str] = field(default_factory=list)
    ui_settings: List[Dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    oidc_id: Optional[str] = None
    auth_type: str = "password"
