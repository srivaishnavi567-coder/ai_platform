# from typing import Optional

# class LangfuseConfig:
#     def __init__(
#         self,
#         public_key: str,
#         secret_key: str,
#         host: str = "https://cloud.langfuse.com"
#     ):
#         self.public_key = public_key
#         self.secret_key = secret_key
#         self.host = host


# # global config holder
# _langfuse_config: Optional[LangfuseConfig] = None


# def set_langfuse_config(config: LangfuseConfig):
#     """
#     Called by SDK user to explicitly configure Langfuse
#     """
#     global _langfuse_config
#     _langfuse_config = config


# def get_langfuse_config() -> Optional[LangfuseConfig]:
#     return _langfuse_config
from typing import Optional


class LangfuseConfig:
    """
    User-provided Langfuse configuration.
    SDK will enable Langfuse ONLY if this is set.
    """

    def __init__(
        self,
        public_key: str,
        secret_key: str,
        host: str = "https://cloud.langfuse.com",
    ):
        if not public_key or not secret_key:
            raise ValueError("Langfuse public_key and secret_key are required")

        self.public_key = public_key
        self.secret_key = secret_key
        self.host = host


# ----------------------------
# Internal global state
# ----------------------------
_langfuse_config: Optional[LangfuseConfig] = None


def set_langfuse_config(config: LangfuseConfig):
    """
    Called by SDK user to enable Langfuse.
    """
    global _langfuse_config
    _langfuse_config = config


def get_langfuse_config() -> Optional[LangfuseConfig]:
    """
    Used internally by SDK.
    """
    return _langfuse_config
