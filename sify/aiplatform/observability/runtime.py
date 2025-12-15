"""
Ensures Langfuse patch is applied exactly once.
"""

from sify.aiplatform.observability.langfuse_patch import apply_langfuse_patch

_PATCHED = False


def ensure_langfuse_patch():
    global _PATCHED
    if not _PATCHED:
        apply_langfuse_patch()
        _PATCHED = True
