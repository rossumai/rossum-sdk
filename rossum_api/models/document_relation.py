from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DocumentRelationType(str, Enum):  # noqa: D101
    EXPORT = "export"
    EINVOICE = "einvoice"


@dataclass
class DocumentRelation:
    """Document relation introduces additional relations between annotations and documents.

    .. warning::
        Please note that Document Relation object and all endpoints associated with it are in beta
        version right now. The API may change in the future.


    An :class:`~rossum_api.models.annotation.Annotation` can be related to one or more
    :class:`~rossum_api.models.document.Document` objects and it may belong to several such relations
    of different types at the same time. These are additional to the main relation between the
    :class:`~rossum_api.models.annotation.Annotation` and the :class:`~rossum_api.models.document.Document`
    from which it was created.

    Arguments
    ---------
    id
        ID of the document relation.
    type
        Type of relationship. Possible values are ``'export', 'einvoice'``.
    annotation
        URL of related :class:`~rossum_api.models.annotation.Annotation`.
    key
        Key used to distinguish several relationships of the same type.
    documents
        List of URLs of related :class:`~rossum_api.models.document.Documnets`.
    url
        URL of the relation.

    Notes
    -----
    The combination of ``type``, ``key`` and ``annotation`` attribute values must be *unique*.

    References
    ----------
    https://elis.rossum.ai/api/docs/#document-relation
    """

    id: int
    type: DocumentRelationType
    annotation: str  # Multiple values may be separated using a comma.
    key: str | None
    documents: list[str]
    url: str
