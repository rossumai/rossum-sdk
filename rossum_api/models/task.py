from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class TaskType(str, Enum):  # noqa: D101
    DOCUMENTS_DOWNLOAD = "documents_download"
    UPLOAD_CREATED = "upload_created"
    EMAIL_IMPORTED = "email_imported"


class TaskStatus(str, Enum):  # noqa: D101
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass
class Task:
    """Tasks are used as status monitors of asynchronous operations.

    Tasks with succeeded status can redirect to the object created as a result of them.
    If ``no_redirect=true`` is passed as a query parameter, endpoint won't redirect to an object
    created, but will return information about the task itself instead.

    .. warning::
        Please note that task object and all endpoints associated with it are in beta version
        right now. The API may change in the future.

    Arguments
    ---------
    id
        ID of task object.
    url
        URL of task object.
    type
        Currently supported options for task types are ``documents_download``, ``upload_created``,
        and ``email_imported``.
    status
        One of ``running``, ``succeeded`` or ``failed``.
    expires_at
        Timestamp of a guaranteed availability of the task object.
        Expired tasks are being deleted periodically.
    content
        Detailed information related to tasks
        (see `tasks content <https://elis.rossum.ai/api/docs/#tasks-content>`_ detail).
    detail
        Detailed message on the status of the task. For failed tasks, error id is included
        in the message and can be used in communication with Rossum support for further investigation.
    code
        Error code.
    result_url
        Succeeded status resulting redirect URL.

    References
    ----------
    https://elis.rossum.ai/api/docs/#task.
    """

    id: int
    url: str
    type: TaskType
    status: TaskStatus
    expires_at: str
    content: dict[str, Any] | None = None
    detail: str | None = None
    code: str | None = None
    result_url: str | None = None
