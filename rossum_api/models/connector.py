from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Connector:
    """Connector is used to configure external or internal endpoint of such an extension service.

    Connector is an extension of Rossum that allows to validate and modify data during validation
    and also export data to an external system.

    Arguments
    ---------
    id
        ID of the connector.
    name
        Name of the connector.
    url
        URL of the connector.
    service_url
        URL of the connector endpoint.
    params
        Query params appended to the ``service_url``.
    client_ssl_certificate
        Client SSL certificate used to authenticate requests. Must be PEM encoded.
    authorization_token
        Token sent to connector in Authorization header to ensure connector was contacted by Rossum.
    client_ssl_key
        Client SSL key (write only). Must be PEM encoded. Key may not be encrypted.
    queues
        List of :class:`~rossum_api.models.queue.Queue` objects that use connector object.
    authorization_type
        Token sent to connector in Authorization header to ensure connector was contacted by Rossum.
    asynchronous
        Affects exporting: when ``True``, confirm endpoint returns immediately and connector's
        save endpoint is called asynchronously later on.
    metadata
        Client data.

    References
    ----------
    https://elis.rossum.ai/api/docs/#connector
    """

    id: int
    name: str
    url: str
    service_url: str
    params: str
    client_ssl_certificate: str
    authorization_token: str
    client_ssl_key: str | None = None
    queues: list[str] = field(default_factory=list)
    authorization_type: str = "secret_key"
    asynchronous: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
