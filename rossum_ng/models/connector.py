from typing import Any, Dict, List, Optional

from pydantic import Field

from rossum_ng.models.base import Base


class Connector(Base):
    id: int
    name: str
    url: str
    service_url: str
    params: str
    client_ssl_certificate: str
    authorization_token: str
    client_ssl_key: Optional[str] = None
    queues: List[str] = Field(default_factory=list)
    authorization_type: str = "secret_key"
    asynchronous: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)
