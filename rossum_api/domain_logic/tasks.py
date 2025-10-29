from __future__ import annotations

from typing import TYPE_CHECKING

from rossum_api.models.task import TaskStatus

if TYPE_CHECKING:
    from rossum_api.utils import ObjectWithStatus


def is_task_succeeded(task: ObjectWithStatus) -> bool:
    return task.status == TaskStatus.SUCCEEDED.value
