# import time
# from functools import wraps
# from typing import Callable

# from sify.aiplatform.langfuse.client import get_langfuse
# from sify.aiplatform.models.model_as_a_service import ModelAsAService


# # -------------------------------------------------
# # Internal helpers
# # -------------------------------------------------

# def _already_patched(fn: Callable) -> bool:
#     return getattr(fn, "_langfuse_patched", False)


# def _mark_patched(fn: Callable):
#     setattr(fn, "_langfuse_patched", True)
#     return fn


# def _start_trace(lf, **kwargs):
#     """
#     Langfuse API compatibility layer.
#     Supports v2 and v3 safely.
#     """
#     if hasattr(lf, "start_trace"):
#         return lf.start_trace(**kwargs)
#     if hasattr(lf, "trace"):
#         return lf.trace(**kwargs)
#     return None


# # -------------------------------------------------
# # Patch: chat_completion
# # -------------------------------------------------

# def _patch_chat_completion():
#     original = ModelAsAService.chat_completion

#     if _already_patched(original):
#         return

#     @wraps(original)
#     def wrapped(self, messages, stream=False, **kwargs):
#         lf = get_langfuse()
#         trace = None
#         start = time.time()

#         if lf and not stream:
#             trace = _start_trace(
#                 lf,
#                 name="chat_completion",
#                 input={
#                     "messages": messages,
#                     "params": kwargs
#                 },
#                 metadata={
#                     "model": self.model_id,
#                     "type": "chat"
#                 }
#             )

#         try:
#             result = original(self, messages, stream=stream, **kwargs)

#             if trace:
#                 trace.generation(
#                     name="chat_completion",
#                     model=self.model_id,
#                     input=messages,
#                     output=str(result),
#                     metadata={
#                         "latency_ms": round((time.time() - start) * 1000, 2),
#                         "status": "success"
#                     }
#                 )
#                 trace.end()

#             return result

#         except Exception as e:
#             if trace:
#                 trace.generation(
#                     name="chat_completion_error",
#                     model=self.model_id,
#                     input=messages,
#                     output=None,
#                     metadata={
#                         "error": str(e),
#                         "latency_ms": round((time.time() - start) * 1000, 2),
#                         "status": "error"
#                     }
#                 )
#                 trace.end()
#             raise

#     ModelAsAService.chat_completion = _mark_patched(wrapped)


# # -------------------------------------------------
# # Patch: completion
# # -------------------------------------------------

# def _patch_completion():
#     original = ModelAsAService.completion

#     if _already_patched(original):
#         return

#     @wraps(original)
#     def wrapped(self, prompt, stream=False, **kwargs):
#         lf = get_langfuse()
#         trace = None
#         start = time.time()

#         if lf and not stream:
#             trace = _start_trace(
#                 lf,
#                 name="completion",
#                 input={
#                     "prompt": prompt,
#                     "params": kwargs
#                 },
#                 metadata={
#                     "model": self.model_id,
#                     "type": "completion"
#                 }
#             )

#         try:
#             result = original(self, prompt, stream=stream, **kwargs)

#             if trace:
#                 trace.generation(
#                     name="completion",
#                     model=self.model_id,
#                     input=prompt,
#                     output=str(result),
#                     metadata={
#                         "latency_ms": round((time.time() - start) * 1000, 2),
#                         "status": "success"
#                     }
#                 )
#                 trace.end()

#             return result

#         except Exception as e:
#             if trace:
#                 trace.generation(
#                     name="completion_error",
#                     model=self.model_id,
#                     input=prompt,
#                     output=None,
#                     metadata={
#                         "error": str(e),
#                         "latency_ms": round((time.time() - start) * 1000, 2),
#                         "status": "error"
#                     }
#                 )
#                 trace.end()
#             raise

#     ModelAsAService.completion = _mark_patched(wrapped)


# -------------------------------------------------
# Public entrypoint
# -------------------------------------------------

# def apply_langfuse_patch():
#     _patch_chat_completion()
#     _patch_completion()

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
        root_span = None
        start = time.time()

        if lf and not stream:
            root_span = lf.start_span(
                name="chat_completion",
                input={
                    "messages": messages,
                    "params": kwargs,
                },
                metadata={
                    "model": self.model_id,
                    "type": "chat",
                },
            )

        try:
            result = original(self, messages, stream=stream, **kwargs)

            if root_span:
                gen_span = lf.start_span(
                    name="chat_completion_generation",
                    trace_id=root_span.trace_id,
                    parent_span_id=root_span.id,
                    input=messages,
                    output=str(result),
                    metadata={
                        "model": self.model_id,
                        "latency_ms": round((time.time() - start) * 1000, 2),
                        "status": "success",
                    },
                )
                gen_span.end()
                root_span.end()

            return result

        except Exception as e:
            if root_span:
                err_span = lf.start_span(
                    name="chat_completion_error",
                    trace_id=root_span.trace_id,
                    parent_span_id=root_span.id,
                    input=messages,
                    metadata={
                        "error": str(e),
                        "latency_ms": round((time.time() - start) * 1000, 2),
                        "status": "error",
                    },
                )
                err_span.end()
                root_span.end()
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
        root_span = None
        start = time.time()

        if lf and not stream:
            root_span = lf.start_span(
                name="completion",
                input={
                    "prompt": prompt,
                    "params": kwargs,
                },
                metadata={
                    "model": self.model_id,
                    "type": "completion",
                },
            )

        try:
            result = original(self, prompt, stream=stream, **kwargs)

            if root_span:
                gen_span = lf.start_span(
                    name="completion_generation",
                    trace_id=root_span.trace_id,
                    parent_span_id=root_span.id,
                    input=prompt,
                    output=str(result),
                    metadata={
                        "model": self.model_id,
                        "latency_ms": round((time.time() - start) * 1000, 2),
                        "status": "success",
                    },
                )
                gen_span.end()
                root_span.end()

            return result

        except Exception as e:
            if root_span:
                err_span = lf.start_span(
                    name="completion_error",
                    trace_id=root_span.trace_id,
                    parent_span_id=root_span.id,
                    input=prompt,
                    metadata={
                        "error": str(e),
                        "latency_ms": round((time.time() - start) * 1000, 2),
                        "status": "error",
                    },
                )
                err_span.end()
                root_span.end()
            raise

    ModelAsAService.completion = _mark_patched(wrapped)


# -------------------------------------------------
# Public entrypoint
# -------------------------------------------------

def apply_langfuse_patch():
    _patch_chat_completion()
    _patch_completion()

