import os
from typing import Optional


from langfuse import Langfuse
from .config import get_langfuse_config

_langfuse_client: Optional[Langfuse] = None


def get_langfuse() -> Optional[Langfuse]:
    global _langfuse_client

    if _langfuse_client:
        return _langfuse_client

    cfg = get_langfuse_config()
    if not cfg:
        return None

    _langfuse_client = Langfuse(
        public_key=cfg.public_key,
        secret_key=cfg.secret_key,
        host=cfg.host,   # http://localhost:3000
    )
    return _langfuse_client
