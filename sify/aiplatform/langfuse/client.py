# import os
# from typing import Optional

# os.environ.setdefault("OTEL_TRACES_EXPORTER", "none")
# os.environ.setdefault("OTEL_METRICS_EXPORTER", "none")
# os.environ.setdefault("OTEL_LOGS_EXPORTER", "none")
# from langfuse import Langfuse

# from .config import get_langfuse_config

# _langfuse_client: Optional[Langfuse] = None


# def get_langfuse() -> Optional[Langfuse]:
#     """
#     Returns a Langfuse client ONLY if user configured it.
#     Priority:
#       1. Explicit LangfuseConfig (recommended)
#       2. Environment variables (if user prefers env-based config)
#       3. None (Langfuse disabled)
#     """
#     global _langfuse_client

#     if _langfuse_client:
#         return _langfuse_client

#     # ----------------------------
#     # 1️⃣ Explicit user config
#     # ----------------------------
#     cfg = get_langfuse_config()
#     if cfg:
#         _langfuse_client = Langfuse(
#             public_key=cfg.public_key,
#             secret_key=cfg.secret_key,
#             host=cfg.host
#         )
#         return _langfuse_client

#     # ----------------------------
#     # 2️⃣ Environment variables
#     # (user is responsible for loading .env)
#     # ----------------------------
#     public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
#     secret_key = os.getenv("LANGFUSE_SECRET_KEY")
#     host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

#     if public_key and secret_key:
#         _langfuse_client = Langfuse(
#             public_key=public_key,
#             secret_key=secret_key,
#             host=host
#         )
#         return _langfuse_client

#     # ----------------------------
#     # 3️⃣ Not configured → disabled
#     # ----------------------------
#     return None
import os
from typing import Optional


# 🔒 HARD DISABLE OTEL (must be BEFORE langfuse import)
os.environ["OTEL_SDK_DISABLED"] = "true"
from langfuse import Langfuse
from .config import get_langfuse_config


_langfuse_client: Optional[Langfuse] = None


def get_langfuse() -> Optional[Langfuse]:
    """
    Returns a Langfuse client ONLY if user configured it.
    """
    global _langfuse_client

    if _langfuse_client:
        return _langfuse_client

    # 1️⃣ Explicit SDK config
    cfg = get_langfuse_config()
    if cfg:
        _langfuse_client = Langfuse(
            public_key=cfg.public_key,
            secret_key=cfg.secret_key,
            host=cfg.host,
        )
        return _langfuse_client

    # 2️⃣ Env-based config
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

    if public_key and secret_key:
        _langfuse_client = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host,
        )
        return _langfuse_client

    return None

