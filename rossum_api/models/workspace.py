from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Workspace:
    """Workspace is a container of `:class:`~rossum_api.models.queue.Queue`.

    Arguments
    ---------
    id
        ID of the workspace.
    name
        Name of the workspace.
    url
        URL of the workspace.
    autopilot
        (Deprecated) Whether to automatically confirm datapoints (hide eyes) from previously seen
        annotations
    organization
        URL of the related `:class:`~rossum_api.models.organization.Organization`.
    queues
        List of `:class:`~rossum_api.models.queue.Queue` that belong to the workspace.
    metadata
        Client data.

    Notes
    -----
    Please note that autopilot configuration has been moved to `:class:`~rossum_api.models.queue.Queue`.
    Option autopilot remains **read-only** on Workspace and represents autopilot configuration
    set to `:class:`~rossum_api.models.queue.Queue` within a workspace.

    References
    ----------
    https://elis.rossum.ai/api/docs/#workspace
    """

    id: int
    name: str
    url: str
    autopilot: bool
    organization: str
    queues: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
