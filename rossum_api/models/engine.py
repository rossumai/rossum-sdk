from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

EngineFieldType = Literal["string", "number", "date", "enum"]
MultilineType = Literal["true", "false", ""]  # Preparation for "auto" option


@dataclass
class Engine:
    """Engine represents an AI extraction engine in Rossum.

    An engine defines the AI model and configuration used for document
    processing and field extraction in Rossum queues.

    Arguments
    ---------
    id
        ID of the engine.
    url
        URL of the engine.
    name
        Name of the engine.
    type
        Type of the engine.
    learning_enabled
        Whether learning is enabled for this engine.
    training_queues
        List of queue URLs where this engine is used for training.
    description
        Description of the engine.
    agenda_id
        ID of the agenda associated with this engine.

    References
    ----------
    (Internal API. No public reference)
    * Model is excluded from Sphinx documentation
    """

    id: int
    url: str
    name: str
    type: Literal["extractor", "splitter"]
    learning_enabled: bool
    training_queues: list[str]
    description: str
    agenda_id: str


@dataclass
class EngineField:
    """EngineField represents a field definition within an AI extraction engine.

    An engine field defines the structure and configuration of a specific
    data field that the AI engine can extract from documents.

    Arguments
    ---------
    id
        ID of the engine field.
    url
        URL of the engine field.
    engine
        URL of the engine this field belongs to.
    name
        Name of the engine field.
    tabular
        Whether this field represents tabular data.
    label
        Display label for the field.
    type
        Type of the field
    subtype
        Subtype specification for the field, if applicable.
    pre_trained_field_id
        ID of the pre-trained field this field is based on, if applicable.
    multiline
        Whether the field supports multiline input.

    References
    ----------
    (Internal API. No public reference)
    * Model is excluded from Sphinx documentation
    """

    id: int
    url: str
    engine: str
    name: str
    tabular: bool
    label: str
    type: EngineFieldType
    subtype: str | None
    pre_trained_field_id: str | None
    multiline: MultilineType
