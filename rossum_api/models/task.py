from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class TaskType(str, Enum):
    DOCUMENTS_DOWNLOAD = "documents_download"
    UPLOAD_CREATED = "upload_created"
    EMAIL_IMPORTED = "email_imported"


class TaskStatus(str, Enum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass
class Task:
    """Represents https://elis.rossum.ai/api/docs/#task."""

    id: int
    url: str
    type: TaskType
    status: TaskStatus
    expires_at: str
    content: Optional[Dict[str, Any]] = None
    detail: Optional[str] = None
    code: Optional[str] = None
    result_url: Optional[str] = None
