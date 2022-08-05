from typing import Any, Dict, List, Optional

from pydantic import Field

from rossum_ng.models.base import Base


class Inbox(Base):
    id: int
    name: str
    url: str
    queues: List[str]
    email: str
    email_prefix: str
    bounce_email_to: Optional[str]
    bounce_unprocessable_attachments: bool = False
    bounce_postponed_annotations: bool = False
    bounce_deleted_annotations: bool = False
    bounce_email_with_no_attachments: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)
    filters: Dict[str, Any] = Field(default_factory=dict)
    dmarc_check_action: str = "accept"
