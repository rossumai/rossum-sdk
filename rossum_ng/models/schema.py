from typing import Dict, List, Optional

from pydantic import Field

from rossum_ng.models.base import Base


class Schema(Base):
    id: int
    name: Optional[str] = None
    queues: List[str] = Field(default_factory=list)
    url: Optional[str] = None
    content: List[Dict] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
