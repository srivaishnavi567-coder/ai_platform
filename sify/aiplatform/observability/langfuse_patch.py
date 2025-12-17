

# import time
# from functools import wraps
# from typing import Callable

# from sify.aiplatform.langfuse.client import get_langfuse
# from sify.aiplatform.models.model_as_a_service import ModelAsAService


# # -------------------------------------------------
# # Helpers
# # -------------------------------------------------

# def _already_patched(fn: Callable) -> bool:
#     return getattr(fn, "_langfuse_patched", False)


# def _mark_patched(fn: Callable):
#     setattr(fn, "_langfuse_patched", True)
#     return fn


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
#         root_span = None
#         start = time.time()

#         if lf and not stream:
#             root_span = lf.start_span(
#                 name="chat_completion",
#                 input={
#                     "messages": messages,
#                     "params": kwargs,
#                 },
#                 metadata={
#                     "model": self.model_id,
#                     "type": "chat",
#                 },
#             )

#         try:
#             result = original(self, messages, stream=stream, **kwargs)

#             if root_span:
#                 gen_span = root_span.start_span(
#                     name="chat_completion_generation",
#                     input=messages,
#                     output=str(result),
#                     metadata={
#                         "model": self.model_id,
#                         "latency_ms": round((time.time() - start) * 1000, 2),
#                         "status": "success",
#                     },
#                 )
#                 gen_span.end()
#                 root_span.end()

#             return result

#         except Exception as e:
#             if root_span:
#                 err_span = root_span.start_span(
#                     name="chat_completion_error",
#                     input=messages,
#                     metadata={
#                         "error": str(e),
#                         "latency_ms": round((time.time() - start) * 1000, 2),
#                         "status": "error",
#                     },
#                 )
#                 err_span.end()
#                 root_span.end()
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
#         root_span = None
#         start = time.time()

#         if lf and not stream:
#             root_span = lf.start_span(
#                 name="completion",
#                 input={
#                     "prompt": prompt,
#                     "params": kwargs,
#                 },
#                 metadata={
#                     "model": self.model_id,
#                     "type": "completion",
#                 },
#             )

#         try:
#             result = original(self, prompt, stream=stream, **kwargs)

#             if root_span:
#                 gen_span = root_span.start_span(
#                     name="completion_generation",
#                     input=prompt,
#                     output=str(result),
#                     metadata={
#                         "model": self.model_id,
#                         "latency_ms": round((time.time() - start) * 1000, 2),
#                         "status": "success",
#                     },
#                 )
#                 gen_span.end()
#                 root_span.end()

#             return result

#         except Exception as e:
#             if root_span:
#                 err_span = root_span.start_span(
#                     name="completion_error",
#                     input=prompt,
#                     metadata={
#                         "error": str(e),
#                         "latency_ms": round((time.time() - start) * 1000, 2),
#                         "status": "error",
#                     },
#                 )
#                 err_span.end()
#                 root_span.end()
#             raise

#     ModelAsAService.completion = _mark_patched(wrapped)


# # -------------------------------------------------
# # Entrypoint
# # -------------------------------------------------

# def apply_langfuse_patch():
#     _patch_chat_completion()
#     _patch_completion()


import time
from functools import wraps
from typing import Callable

from sify.aiplatform.langfuse.client import get_langfuse
from sify.aiplatform.models.model_as_a_service import ModelAsAService


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def _already_patched(fn: Callable) -> bool:
    return getattr(fn, "_langfuse_patched", False)


def _mark_patched(fn: Callable):
    setattr(fn, "_langfuse_patched", True)
    return fn


# -------------------------------------------------
# Patch: chat_completion (NON-BREAKING)
# -------------------------------------------------

def _patch_chat_completion():
    original = ModelAsAService.chat_completion

    if _already_patched(original):
        return

    @wraps(original)
    def wrapped(self, messages, stream=False, **kwargs):
        lf = get_langfuse()
        start = time.time()

        trace = generation = None

        # ⚠️ DO NOT TRACE STREAMING (safe behavior, unchanged)
        if lf and not stream:
            trace = lf.trace(
                name="chat_completion",
                metadata={
                    "model": self.model_id,
                    "type": "chat",
                },
            )

            generation = trace.generation(
                name="chat_completion_generation",
                model=self.model_id,
                input={
                    "messages": messages,
                    "params": kwargs,
                },
            )

        try:
            result = original(self, messages, stream=stream, **kwargs)

            if generation:
                output_text = None
                usage = None

                try:
                    output_text = result.choices[0].message.content
                    usage = result.usage.__dict__ if result.usage else None
                except Exception:
                    output_text = str(result)

                generation.end(
                    output=output_text,
                    usage=usage,
                    metadata={
                        "latency_ms": round((time.time() - start) * 1000, 2),
                        "status": "success",
                    },
                )

            return result

        except Exception as e:
            if generation:
                generation.end(
                    status="error",
                    metadata={
                        "error": str(e),
                        "latency_ms": round((time.time() - start) * 1000, 2),
                    },
                )
            raise

    ModelAsAService.chat_completion = _mark_patched(wrapped)


# -------------------------------------------------
# Patch: completion (NON-BREAKING)
# -------------------------------------------------

def _patch_completion():
    original = ModelAsAService.completion

    if _already_patched(original):
        return

    @wraps(original)
    def wrapped(self, prompt, stream=False, **kwargs):
        lf = get_langfuse()
        start = time.time()

        trace = generation = None

        if lf and not stream:
            trace = lf.trace(
                name="completion",
                metadata={
                    "model": self.model_id,
                    "type": "completion",
                },
            )

            generation = trace.generation(
                name="completion_generation",
                model=self.model_id,
                input={
                    "prompt": prompt,
                    "params": kwargs,
                },
            )

        try:
            result = original(self, prompt, stream=stream, **kwargs)

            if generation:
                output_text = None
                usage = None

                try:
                    output_text = result.choices[0].text
                    usage = result.usage.__dict__ if result.usage else None
                except Exception:
                    output_text = str(result)

                generation.end(
                    output=output_text,
                    usage=usage,
                    metadata={
                        "latency_ms": round((time.time() - start) * 1000, 2),
                        "status": "success",
                    },
                )

            return result

        except Exception as e:
            if generation:
                generation.end(
                    status="error",
                    metadata={
                        "error": str(e),
                        "latency_ms": round((time.time() - start) * 1000, 2),
                    },
                )
            raise

    ModelAsAService.completion = _mark_patched(wrapped)


# -------------------------------------------------
# Entrypoint
# -------------------------------------------------

def apply_langfuse_patch():
    _patch_chat_completion()
    _patch_completion()
