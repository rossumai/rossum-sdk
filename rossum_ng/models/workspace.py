from typing import Any, Dict, List

from pydantic import Field

from rossum_ng.models.base import Base


class Workspace(Base):
    id: int
    name: str
    url: str
    autopilot: bool
    organization: str
    queues: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
