from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Document:
    """Document contains information about one input file.

    Arguments
    ---------
    id
        ID of the document.
    url
        URL of the document.
    s3_name
        Internal name of object name in S3.
    parent
        URL of the parent document (e.g. the zip file it was extracted from).
    email
        URL of the email object that document was imported by (only for documents imported by email).
    mime_type
        MIME type of the document, e.g. ``application/pdf``.
    creator
        URL of :class:`~rossum_api.models.user.User` that created the annotation.
    created_at
        Timestamp of document upload or incoming email attachment extraction.
    arrived_at
        Deprecated. See ``created_at``.
    original_file_name
        File name of the attachment or upload.
    content
        Link to the document's raw content (e.g. PDF file). May be null if there is no file associated.
    metadata
        Client data.
    annotations
        List of URLs of :class:`~rossum_api.models.annotation.Annotation` objects related to the document.
        Usually there is only one annotation.
    attachment_status
        Reason, why the document got filtered out on Email ingestion. See attachment status

    References
    ----------
    https://elis.rossum.ai/api/docs/#document
    """

    id: int
    url: str
    s3_name: str
    parent: str | None
    email: str | None
    mime_type: str
    creator: str | None
    created_at: str
    arrived_at: str
    original_file_name: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    annotations: list[str] = field(default_factory=list)
    attachment_status: str | None = None
