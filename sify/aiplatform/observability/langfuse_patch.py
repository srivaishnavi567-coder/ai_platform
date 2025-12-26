

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
import os
from functools import wraps
from typing import Callable

from langfuse import propagate_attributes
from sify.aiplatform.langfuse.client import get_langfuse
from sify.aiplatform.models.model_as_a_service import ModelAsAService


def _already_patched(fn: Callable) -> bool:
    return getattr(fn, "_langfuse_patched", False)


def _mark_patched(fn: Callable):
    setattr(fn, "_langfuse_patched", True)
    return fn


def _get_context():
    return {
        "user_id": os.getenv("LANGFUSE_USER_ID"),
        "session_id": os.getenv("LANGFUSE_SESSION_ID"),
    }


# -------------------------------------------------
# chat_completion patch (TOKENS FIXED)
# -------------------------------------------------

def _patch_chat_completion():
    original = ModelAsAService.chat_completion
    if _already_patched(original):
        return

    @wraps(original)
    def wrapped(self, messages, stream=False, **kwargs):
        lf = get_langfuse()
        start = time.time()
        ctx = _get_context()

        if not lf or stream:
            return original(self, messages, stream=stream, **kwargs)

        with lf.start_as_current_observation(
            as_type="span",
            name="chat_completion",
            input={"messages": messages, "params": kwargs},
            metadata={"model": self.model_id},
        ):
            with propagate_attributes(
                user_id=ctx["user_id"],
                session_id=ctx["session_id"],
            ):
                result = original(self, messages, stream=stream, **kwargs)

                # Extract output
                output = result.choices[0].message.content

                # Extract token usage (MAAS-compatible)
                usage_details = None
                if getattr(result, "usage", None):
                    usage_details = {
                        "input": result.usage.prompt_tokens,
                        "output": result.usage.completion_tokens,
                        # total auto-derived
                    }

                # ✅ Proper GENERATION with tokens
                with lf.start_as_current_observation(
                    as_type="generation",
                    name="chat_completion_generation",
                    input=messages,
                    model=self.model_id,
                ):
                    lf.update_current_generation(
                        output={
                            "role": "assistant",
                            "content": output,
                        },
                        usage_details=usage_details,
                        metadata={
                            "latency_ms": round((time.time() - start) * 1000, 2)
                        },
                    )

                return result

    ModelAsAService.chat_completion = _mark_patched(wrapped)


# -------------------------------------------------
# completion patch (TOKENS FIXED)
# -------------------------------------------------

def _patch_completion():
    original = ModelAsAService.completion
    if _already_patched(original):
        return

    @wraps(original)
    def wrapped(self, prompt, stream=False, **kwargs):
        lf = get_langfuse()
        start = time.time()
        ctx = _get_context()

        if not lf or stream:
            return original(self, prompt, stream=stream, **kwargs)

        with lf.start_as_current_observation(
            as_type="span",
            name="completion",
            input={"prompt": prompt, "params": kwargs},
            metadata={"model": self.model_id},
        ):
            with propagate_attributes(
                user_id=ctx["user_id"],
                session_id=ctx["session_id"],
            ):
                result = original(self, prompt, stream=stream, **kwargs)

                output = result.choices[0].text

                usage_details = None
                if getattr(result, "usage", None):
                    usage_details = {
                        "input": result.usage.prompt_tokens,
                        "output": result.usage.completion_tokens,
                    }

                with lf.start_as_current_observation(
                    as_type="generation",
                    name="completion_generation",
                    input=prompt,
                    model=self.model_id,
                ):
                    lf.update_current_generation(
                        output=output,
                        usage_details=usage_details,
                        metadata={
                            "latency_ms": round((time.time() - start) * 1000, 2)
                        },
                    )

                return result

    ModelAsAService.completion = _mark_patched(wrapped)


def apply_langfuse_patch():
    _patch_chat_completion()
    _patch_completion()




