from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal

EmailLabel = Literal[
    "rejection",
    "automatic_rejection",
    "rejected",
    "automatic_status_changed_info",
    "forwarded",
    "reply",
]


class EmailType(str, Enum):  # noqa: D101
    INCOMING = "incoming"
    OUTGOING = "outgoing"


@dataclass
class Email:
    """Email represents emails sent to Rossum inboxes.

    Arguments
    ---------
    id
        ID of the email.
    url
        URL of the email.
    queue
        URL of the associated :class:`~rossum_api.models.queue.Queue`.
    inbox
        URL of the associated :class:`~rossum_api.models.inbox.Inbox`.
    parent
        URL of the parent email.
    email_thread
        URL of the associated email thread.
    children
        List of URLs of the children emails.
    documents
        List of URLs of :class:`~rossum_api.models.document.Document` objects attached to the email.
    created_at
        Timestamp of incoming email.
    last_thread_email_created_at
        (Deprecated) Timestamp of the most recent email in this email thread.
    subject
    from_
        Information about sender containing keys ``email`` and ``name``.
    to
        List that contains information about recipients.
    cc
        List that contains information about recipients of carbon copy.
    bcc
        List that contains information about recipients of blind carbon copy.
    body_text_plain
        Plain text email section (shortened to 4kB).
    body_text_html
        HTML email section (shortened to 4kB).
    metadata
        Client data.
    type
        Email type. Can be ``incoming`` or ``outgoing``.
    annotation_counts
        Information about how many annotations were extracted from email attachments
        and in which state they currently are.
        This attribute is intended for **INTERNAL** use only and may be changed in the future.
    annotations
        List of URLs of :class:`~rossum_api.models.annotation.Annotation` objects that arrived via email
    related_annotations
        List of URLs of :class:`~rossum_api.models.annotation.Annotation` objects that are related
        to the email (e.g. rejected by that, added as attachment etc.).
    related_documents
        List of URLs of :class:`~rossum_api.models.document.Document` objects related to the email,
        (e.g. by forwarding email containing document as attachment etc.).
    creator
        :class:`~rossum_api.models.user.User` that have sent the email.
        ``None`` if email has been received via SMTP.
    filtered_out_document_count
        Number of documents automatically filtered out by Rossum smart inbox.
        This attribute is intended for **INTERNAL** use only and may be changed in the future.
    labels
        List of email labels.
    content
        URL of the emails content.

    References
    ----------
    https://elis.rossum.ai/api/docs/#email
    """

    id: int
    url: str
    queue: str
    inbox: str
    parent: str | None
    email_thread: str | None
    children: list[str]
    documents: list[str]
    created_at: str | None = None
    last_thread_email_created_at: str | None = None
    subject: str | None = None
    # "from" is converted to "from_" during the deserialization, see rossum_api.models._convert_key function.
    from_: dict[str, Any] = field(default_factory=dict)
    to: list[dict[str, Any]] = field(default_factory=list)
    cc: list[dict[str, Any]] = field(default_factory=list)
    bcc: list[dict[str, Any]] = field(default_factory=list)
    body_text_plain: str | None = None
    body_text_html: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    type: EmailType | None = None
    annotation_counts: dict[str, Any] = field(default_factory=dict)
    annotations: list[str] = field(default_factory=list)
    related_annotations: list[str] = field(default_factory=list)
    related_documents: list[str] = field(default_factory=list)
    creator: str | None = None
    filtered_out_document_count: int | None = None
    labels: list[EmailLabel] = field(default_factory=list)
    content: str | None = None
