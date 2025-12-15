import time
from functools import wraps
from typing import Callable

from sify.aiplatform.langfuse.client import get_langfuse
from sify.aiplatform.models.model_as_a_service import ModelAsAService


# -------------------------------------------------
# Internal helpers
# -------------------------------------------------

def _already_patched(fn: Callable) -> bool:
    return getattr(fn, "_langfuse_patched", False)


def _mark_patched(fn: Callable):
    setattr(fn, "_langfuse_patched", True)
    return fn


# -------------------------------------------------
# Patch: chat_completion
# -------------------------------------------------

def _patch_chat_completion():
    original = ModelAsAService.chat_completion

    if _already_patched(original):
        return

    @wraps(original)
    def wrapped(self, messages, stream=False, **kwargs):
        lf = get_langfuse()
        trace = None
        start = time.time()

        # Create trace BEFORE calling MAAS
        if lf and not stream:
            trace = lf.trace(
                name="chat_completion",
                input={
                    "messages": messages,
                    "params": kwargs
                },
                metadata={
                    "model": self.model_id
                }
            )

        try:
            result = original(self, messages, stream=stream, **kwargs)

            if trace:
                trace.generation(
                    name="chat_completion",
                    model=self.model_id,
                    input=messages,
                    output=str(result),
                    metadata={
                        "latency_ms": (time.time() - start) * 1000
                    }
                )
                trace.end()

            return result

        except Exception as e:
            # ERROR TRACE (this is your current case)
            if trace:
                trace.generation(
                    name="chat_completion_error",
                    model=self.model_id,
                    input=messages,
                    output=None,
                    metadata={
                        "error": str(e),
                        "latency_ms": (time.time() - start) * 1000
                    }
                )
                trace.end()
            raise

    ModelAsAService.chat_completion = _mark_patched(wrapped)


# -------------------------------------------------
# Patch: completion
# -------------------------------------------------

def _patch_completion():
    original = ModelAsAService.completion

    if _already_patched(original):
        return

    @wraps(original)
    def wrapped(self, prompt, stream=False, **kwargs):
        lf = get_langfuse()
        trace = None
        start = time.time()

        if lf and not stream:
            trace = lf.trace(
                name="completion",
                input={
                    "prompt": prompt,
                    "params": kwargs
                },
                metadata={
                    "model": self.model_id
                }
            )

        try:
            result = original(self, prompt, stream=stream, **kwargs)

            if trace:
                trace.generation(
                    name="completion",
                    model=self.model_id,
                    input=prompt,
                    output=str(result),
                    metadata={
                        "latency_ms": (time.time() - start) * 1000
                    }
                )
                trace.end()

            return result

        except Exception as e:
            if trace:
                trace.generation(
                    name="completion_error",
                    model=self.model_id,
                    input=prompt,
                    output=None,
                    metadata={
                        "error": str(e),
                        "latency_ms": (time.time() - start) * 1000
                    }
                )
                trace.end()
            raise

    ModelAsAService.completion = _mark_patched(wrapped)


# -------------------------------------------------
# Public entrypoint
# -------------------------------------------------

def apply_langfuse_patch():
    """
    Apply Langfuse monkey patches to ModelAsAService.
    Safe to call multiple times.
    """
    _patch_chat_completion()
    _patch_completion()
