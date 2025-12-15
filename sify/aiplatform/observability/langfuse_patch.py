import time
from functools import wraps
from sify.aiplatform.langfuse.client import get_langfuse
from sify.aiplatform.models.maas import ModelAsAService


def _patch_chat_completion():
    original = ModelAsAService.chat_completion

    @wraps(original)
    def wrapped(self, messages, stream=False, **kwargs):
        lf = get_langfuse()
        trace = None
        start = time.time()

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
                    name="chat_completion_call",
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

    ModelAsAService.chat_completion = wrapped


def _patch_completion():
    original = ModelAsAService.completion

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
                    name="completion_call",
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

    ModelAsAService.completion = wrapped


def apply_langfuse_patch():
    """
    Called once to patch SDK methods
    """
    _patch_chat_completion()
    _patch_completion()
