import os
from langfuse import Langfuse
from .config import get_langfuse_config

_langfuse = None


def get_langfuse():
    global _langfuse

    if _langfuse:
        return _langfuse

    # 1️⃣ Check explicit user config first
    cfg = get_langfuse_config()
    if cfg:
        _langfuse = Langfuse(
            public_key=cfg.public_key,
            secret_key=cfg.secret_key,
            host=cfg.host
        )
        return _langfuse

    # 2️⃣ Fallback to environment variables
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

    if not public_key or not secret_key:
        return None  # Langfuse disabled

    _langfuse = Langfuse(
        public_key=public_key,
        secret_key=secret_key,
        host=host
    )
    return _langfuse
