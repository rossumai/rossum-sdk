from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class EmailTemplate:
    """Email template represents templates one can choose from when sending an email from Rossum.

    Arguments
    ---------
    id
        ID of the email template.
    name
        Name of the email template.
    url
        URL of the email template.
    queue
        URL of the associated :class:`~rossum_api.models.queue.Queue`.
    organization
        URL of the associated :class:`~rossum_api.models.organization.Organization`.
    subject
        Email subject.
    message
        Name of the email template.
    type
        Type of the email template.
    enabled
        (Deprecated). Use ``automate`` instead.
    automate
        True if user wants to send email automatically on the action, see ``type``.
    triggers
        URLs of the linked triggers.
        Read more about `triggers <https://elis.rossum.ai/api/docs/#using-triggers>`_.
    to
        List that contains information about recipients.
    cc
        List that contains information about recipients of carbon copy.
    bcc
        List that contains information about recipients of blind carbon copy.

    References
    ----------
    https://elis.rossum.ai/api/docs/#email-template.

    https://elis.rossum.ai/api/docs/#using-triggers.
    """

    id: int
    name: str
    url: str
    queue: str
    organization: str
    subject: str
    message: str
    type: Literal[
        "rejection", "rejection_default", "email_with_no_processable_attachments", "custom"
    ]
    enabled: bool
    automate: bool
    triggers: list[str] = field(default_factory=list)
    to: list[dict[str, Any]] = field(default_factory=list)
    cc: list[dict[str, Any]] = field(default_factory=list)
    bcc: list[dict[str, Any]] = field(default_factory=list)
