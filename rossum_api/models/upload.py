from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Upload:
    """Represent an upload.

    Arguments
    ---------
    id
        ID of upload object.
    url
        URL of upload object.
    queue
        URL of the target :class:`~rossum_api.models.queue.Queue` of the upload.
    organization
        URL of related :class:`~rossum_api.models.organization.Organization`.
    creator
        URL of the :class:`~rossum_api.models.user.User` who created the upload.
    created_at
        Time of the creation of the upload.
    documents
        URLs of the uploaded :class:`~rossum_api.models.document.Document`.
    additional_documents
        URLs of additional :class:`~rossum_api.models.document.Document` created in ``upload.created``
        event hooks.
    annotations
        URLs of all created :class:`~rossum_api.models.annotation.Annotation`.
    email
        URL of the :class:`~rossum_api.models.email.Email` that created the upload object.

    References
    ----------
    https://elis.rossum.ai/api/docs/#upload.
    """

    id: int
    url: str
    queue: str
    organization: str
    creator: str
    created_at: str
    documents: list[str]
    additional_documents: list[str] = field(default_factory=list)
    annotations: list[str] = field(default_factory=list)
    email: str | None = None
