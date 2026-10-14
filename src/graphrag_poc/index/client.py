"""Qdrant client that does not send localhost through a system proxy."""

import os
from urllib.parse import urlparse

from qdrant_client import QdrantClient


def configure_no_proxy(url: str) -> None:
    """Keep the local Qdrant port off the system HTTP proxy."""

    host = urlparse(url).hostname
    extras = [item for item in (host, "localhost", "127.0.0.1") if item]
    for key in ("NO_PROXY", "no_proxy"):
        current = [part.strip() for part in os.environ.get(key, "").split(",") if part.strip()]
        for item in extras:
            if item not in current:
                current.append(item)
        os.environ[key] = ",".join(current)


def make_client(
    url: str | None = None,
    api_key: str | None = None,
    timeout: int = 120,
) -> QdrantClient:
    address = url or os.environ.get("QDRANT_URL", "http://127.0.0.1:6333")
    configure_no_proxy(address)
    return QdrantClient(url=address, api_key=api_key, timeout=timeout)
