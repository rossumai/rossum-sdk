from __future__ import annotations

from typing import Any


def build_email_import_files(
    raw_message: bytes, recipient: str, mime_type: str | None = None
) -> dict[str, Any]:
    """Build the files dict for the email import endpoint."""
    raw_message_value = ["email.eml", raw_message]
    if mime_type:
        raw_message_value.append(mime_type)

    return {
        "raw_message": tuple(raw_message_value),
        "recipient": (None, recipient),
    }
