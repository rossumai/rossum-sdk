from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from rossum_api.models.automation_blocker import AutomationBlocker
from rossum_api.models.document import Document
from rossum_api.models.user import User


@dataclass
class Prediction:
    """Internal only description of prediction source and version."""

    source: str
    version: str | None = None


@dataclass
class Annotation:
    """Annotation contains all extracted and verified data related to a document.

    Every document belongs to a :class:`~rossum_api.models.queue.Queue` and is related
    to the :class:`~rossum_api.models.schema.Schema`, that defines datapoint types and overall shape
    of the extracted data.

    Arguments
    ---------
    url
        URL of the annotation object.
    status
        Current status of the annotation. See `Annotation Lifecycle <https://elis.rossum.ai/api/docs/#annotation-lifecycle>`_
        for possible values.
    schema
        URL of the schema object.
    modifier
        URL of the user object that last modified the annotation.
    content
        URL of the annotation content.
    id
        Annotation ID.
    queue
        URL of the queue object.
    creator
        URL of the user object that created the annotation.
    created_at
        Timestamp of when the annotation was created.
    rir_poll_id
        Internal extractor processing ID.
    email
        URL of the email object associated with the annotation.
    email_thread
        URL of the email thread object.
    has_email_thread_with_replies
        Boolean indicating if the annotation's email thread has replies.
    has_email_thread_with_new_replies
        Boolean indicating if the annotation's email thread has new replies.
    suggested_edit
        A suggested edit for the annotation.
    messages
        List of messages associated with the annotation.
    time_spent
        Total time spent on the annotation in seconds.
    relations
        List of relations.
    pages
        List of page URLs.
    document
        URL of the document object.
    confirmed_at
        Timestamp of when the annotation was confirmed.
    modified_at
        Timestamp of when the annotation was last modified.
    exported_at
        Timestamp of when the annotation was exported.
    arrived_at
        Timestamp when the annotation arrived.
    assigned_at
        Timestamp of when the annotation was assigned to a user.
    purged_at
        Timestamp of when the annotation was purged.
    rejected_at
        Timestamp of when the annotation was rejected.
    deleted_at
        Timestamp of when the annotation was deleted.
    export_failed_at
        Timestamp of when the annotation export failed.
    organization
        URL of the organization object.
    metadata
        Custom data attached to the annotation.
    automated
        Indicates if the annotation was processed automatically.
    automation_blocker
        URL of the automation blocker object.
    related_emails
        List of related email URLs.
    automatically_rejected
        Indicates if the annotation was automatically rejected.
    prediction
        Internal description of prediction source and version.
    assignees
        List of URLs referencing users assigned to this annotation.
    labels
        List of labels associated with this annotation.
    restricted_access
        Indicates if the annotation has restricted access.
    training_enabled
        Indicates if training is enabled for this annotation.
    einvoice
        Indicates if this is an e-invoice annotation.
    purged_by
        URL of the user object that purged the annotation.
    rejected_by
        URL of the user object that rejected the annotation.
    deleted_by
        URL of the user object that deleted the annotation.
    exported_by
        URL of the user object that exported the annotation.
    confirmed_by
        URL of the user object that confirmed the annotation.
    modified_by
        URL of the user object that last modified the annotation.

    References
    ----------
    https://elis.rossum.ai/api/docs/#annotation.
    """

    url: str
    status: str
    schema: str
    modifier: str | User | None
    content: list[dict[str, Any]] | str  # No dataclass for Annotation content yet
    id: int | None = None
    queue: str | None = None
    creator: str | None = None
    created_at: str | None = None
    rir_poll_id: str | None = None
    email: str | None = None
    email_thread: str | None = None
    has_email_thread_with_replies: bool = False
    has_email_thread_with_new_replies: bool = False
    suggested_edit: str | None = None
    messages: list[dict] | None = None
    time_spent: float | None = 0
    relations: list[str] = field(default_factory=list)
    pages: list[str] = field(default_factory=list)
    document: str | Document | None = None
    confirmed_at: str | None = None
    modified_at: str | None = None
    exported_at: str | None = None
    arrived_at: str | None = None
    assigned_at: str | None = None
    purged_at: str | None = None
    rejected_at: str | None = None
    deleted_at: str | None = None
    export_failed_at: str | None = None
    organization: str | None = None
    metadata: dict[Any, Any] = field(default_factory=dict)
    automated: bool = False
    automation_blocker: AutomationBlocker | str | None = None
    related_emails: list[str] = field(default_factory=list)
    automatically_rejected: bool | None = None
    prediction: Prediction | None = None
    assignees: list[str] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
    restricted_access: bool | None = None
    training_enabled: bool | None = None
    einvoice: bool | None = None
    purged_by: str | None = None
    rejected_by: str | None = None
    deleted_by: str | None = None
    exported_by: str | None = None
    confirmed_by: str | None = None
    modified_by: str | None = None
