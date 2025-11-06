from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class Inbox:
    """Inbox enables email ingestion to a related :class:`~rossum_api.models.queue.Queue`.

    We enforce email domain to match Rossum domain (e.g. .rossum.app). email_prefix may be
    used to construct unique email address.

    Arguments
    ---------
    id
        ID of the inbox.
    name
        Name of the inbox.
    url
        URL of the inbox.
    queues
        :class:`~rossum_api.models.queue.Queue` that receives documents from inbox.
        :class:`~rossum_api.models.queue.Queue` has to be passed in list due to backward compatibility.
        It is possible to have only one queue per inbox.
    email
        Rossum email address (e.g. ``east-west-trading-co-a34f3a@<example>.rossum.app``)
    email_prefix
        Rossum email address prefix (e.g. ``east-west-trading-co``).
        Maximum length allowed is 57 chars.
    bounce_email_to
        (Deprecated) Email address to send notifications to (e.g. about failed import).
        Configuration moved to `Email notifications settings <https://elis.rossum.ai/api/docs/#email-notification-settings>`_.
    bounce_unprocessable_attachments
        (Deprecated) Whether return back unprocessable attachments (e.g. MS Word docx)
        or just silently ignore them. When true, minimum image size requirement does not apply.
        Configuration moved to `Email notifications settings <https://elis.rossum.ai/api/docs/#email-notification-settings>`_.
    bounce_postponed_annotations
        (Deprecated) Whether to send notification when annotation is postponed.
        Configuration moved to `Email notifications settings <https://elis.rossum.ai/api/docs/#email-notification-settings>`_.
    bounce_deleted_annotations
        (Deprecated) Whether to send notification when annotation is deleted.
        Configuration moved to `Email notifications settings <https://elis.rossum.ai/api/docs/#email-notification-settings>`_.
    bounce_email_with_no_attachments
        (Deprecated) Whether to send notification when no processable documents were found.
        Configuration moved to `Email notifications settings <https://elis.rossum.ai/api/docs/#email-notification-settings>`_.
    metadata
        Client data.
    filters
    dmarc_check_action
        Decides what to do with incoming emails, that don't pass the DMARC check.

    References
    ----------
    https://elis.rossum.ai/api/docs/#inbox

    https://elis.rossum.ai/api/docs/#email-notification-settings
    """

    id: int
    name: str
    url: str
    queues: list[str]
    email: str
    email_prefix: str
    bounce_email_to: str | None
    bounce_unprocessable_attachments: bool = False
    bounce_postponed_annotations: bool = False
    bounce_deleted_annotations: bool = False
    bounce_email_with_no_attachments: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
    filters: dict[str, Any] = field(default_factory=dict)
    dmarc_check_action: Literal["accept", "drop"] = "accept"
