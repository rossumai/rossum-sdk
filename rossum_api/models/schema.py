from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Schema:
    """Schema specifies the set of datapoints that are extracted from the document.

    For more information see `Document Schema <https://elis.rossum.ai/api/docs/#document-schema>`_.

    Arguments
    ---------
    id
        ID of the schema.
    name
        Name of the schema.
    queues
        List of :class:`~rossum_api.models.queue.Queue` objects that use schema object.
    url
        URL of the schema.
    content
        List of sections (top-level schema objects, see `Document Schema <https://elis.rossum.ai/api/docs/#document-schema>`_
        for description of schema).
    metadata
        Client data.

    References
    ----------
    https://elis.rossum.ai/api/docs/#schema
    """

    id: int
    name: str | None = None
    queues: list[str] = field(default_factory=list)
    url: str | None = None
    content: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
