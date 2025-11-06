from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Queue:
    """Queue represents a document processing queue in Rossum.

    A queue defines the document processing workflow and connects documents
    to their extraction schema, processing inbox, and user groups.

    Arguments
    ---------
    id
        Id of the queue.
    name
        Name of the queue (max. 255 characters).
    url
        URL of the queue.
    workspace
        Workspace in which the queue should be placed (it can be set to null, but bear in mind
        that it will make the queue invisible in the Rossum UI and it may cause some unexpected consequences).
    connector
        Connector associated with the queue.
    schema
        Schema which will be applied to annotations in this queue.
    inbox
        Inbox for import to this queue.
    counts
        Count of annotations per status.
    session_timeout
        Time before annotation will be returned from reviewing status to to_review
        (timeout is evaluated every 10 minutes). Defaults to 1 hour.
    webhooks
        (Deprecated) Webhooks associated with the queue (serves as an alias for hooks attribute).
    hooks
        Hooks associated with the queue.
    users
        Users associated with this queue.
    rir_url
        (Deprecated) Use generic_engine or dedicated_engine to set AI Core Engine.
    rir_params
        URL parameters to be passed to the AI Core Engine.
    automation_enabled
        Toggle for switching automation on/off.
    automation_level
        Set level of automation.
    default_score_threshold
        Threshold used to automatically validate field content based on AI confidence scores.
    locale
        Typical originating region of documents processed in this queue specified in the locale format.
        If auto option is chosen, the locale will be detected automatically if the organization group
        has access to Aurora engine. Otherwise, default option (en_GB) will be used.
    metadata
        Client data.
    settings
        Queue UI settings.
    dedicated_engine
        Dedicated engine used for processing documents uploaded to this queue. If dedicated_engine
        is set generic_engine must be null.
    generic_engine
        Generic engine used for processing documents uploaded to this queue. If generic_engine
        is set dedicated_engine must be null. If both engines are null, a default generic one gets set.
    use_confirmed_state
        Affects exporting: when true, confirm endpoint transitions annotation to confirmed status
        instead to exporting.
    document_lifetime
        Data retention period -- annotations will be automatically purged this time after their creation.
        The format of the value is '[DD] [HH:[MM:]]ss[.uuuuuu]', e.g. 90 days retention can be set as
        '90 00:00:00'. Please keep in mind that purging documents in Rossum can limit its learning capabilities.
    delete_after
        For internal use only (When a queue is marked for its deletion it will be done after this date).
    status
        Current status of the queue.
    engine
        Engine associated with the queue.
    training_enabled
        Indicates if training is enabled for this queue.

    References
    ----------
    https://elis.rossum.ai/api/docs/#queue.
    """

    id: int
    name: str
    url: str
    workspace: str | None
    connector: str | None
    schema: str
    inbox: str | None
    counts: dict[str, int]
    session_timeout: str = "01:00:00"
    webhooks: list[str] = field(default_factory=list)
    hooks: list[str] = field(default_factory=list)
    users: list[str] = field(default_factory=list)
    rir_url: str | None = None
    rir_params: str | None = None
    automation_enabled: bool = False
    automation_level: str = "never"
    default_score_threshold: float = 0.8
    locale: str = "en_GB"
    metadata: dict[str, Any] = field(default_factory=dict)
    settings: dict[str, Any] = field(default_factory=dict)
    dedicated_engine: str | dict[str, Any] | None = None
    generic_engine: str | dict[str, Any] | None = None
    use_confirmed_state: bool = False
    document_lifetime: str | None = None
    delete_after: str | None = None
    status: str | None = None
    engine: str | None = None
    training_enabled: bool = True
