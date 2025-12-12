from typing import Any, Dict, List, Optional, Union
import json

class ModelInfo:
    id: str
    name: str
    model_type: str
    max_tokens: Optional[int] = None
    dimensions: Optional[int] = None
    language: Optional[List[str]] = None

    def __init__(self, id: str, name: str, model_type: str, max_tokens: Optional[int] = None,
                 dimensions: Optional[int] = None, language: Optional[List[str]] = None, **kwargs):
        self.id = id
        self.name = name
        self.model_type = model_type
        self.max_tokens = max_tokens
        self.dimensions = dimensions
        self.language = language

        # Store any additional fields
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "name": self.name,
            "model_type": self.model_type
        }
        if self.max_tokens is not None:
            result["max_tokens"] = self.max_tokens
        if self.dimensions is not None:
            result["dimensions"] = self.dimensions
        if self.language is not None:
            result["language"] = self.language
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelInfo":
        return cls(**data)

class ModelsListResponse:
    """Response object for listing models."""
    models: List[ModelInfo]

    def __init__(self, models: List[ModelInfo]):
        self.models = models

    def to_dict(self) -> Dict[str, Any]:
        return {
            "models": [model.to_dict() for model in self.models]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelsListResponse":
        models = [ModelInfo.from_dict(model_data) for model_data in data.get("models", [])]
        return cls(models=models)

class EmbeddingData:
    """Individual embedding data."""
    object: str
    embedding: List[float]
    index: int

    def __init__(self, object: str, embedding: List[float], index: int):
        self.object = object
        self.embedding = embedding
        self.index = index

    def to_dict(self) -> Dict[str, Any]:
        return {
            "object": self.object,
            "embedding": self.embedding,
            "index": self.index
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EmbeddingData":
        return cls(
            object=data["object"],
            embedding=data["embedding"],
            index=data["index"]
        )

class EmbeddingUsage:
    """Usage statistics for embeddings."""
    prompt_tokens: int
    total_tokens: int

    def __init__(self, prompt_tokens: int, total_tokens: int):
        self.prompt_tokens = prompt_tokens
        self.total_tokens = total_tokens

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "total_tokens": self.total_tokens
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EmbeddingUsage":
        return cls(
            prompt_tokens=data["prompt_tokens"],
            total_tokens=data["total_tokens"]
        )

class EmbeddingResponse:
    """Response object for embeddings."""
    object: str
    data: List[EmbeddingData]
    model: str
    usage: EmbeddingUsage

    def __init__(self, object: str, data: List[EmbeddingData], model: str, usage: EmbeddingUsage):
        self.object = object
        self.data = data
        self.model = model
        self.usage = usage

    def to_dict(self) -> Dict[str, Any]:
        return {
            "object": self.object,
            "data": [item.to_dict() for item in self.data],
            "model": self.model,
            "usage": self.usage.to_dict()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EmbeddingResponse":
        embedding_data = [EmbeddingData.from_dict(item) for item in data["data"]]
        usage = EmbeddingUsage.from_dict(data["usage"])
        return cls(
            object=data["object"],
            data=embedding_data,
            model=data["model"],
            usage=usage
        )

class ChatMessage:
    """Chat message object."""
    role: str
    content: str

    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatMessage":
        return cls(role=data["role"], content=data["content"])

class ChatChoice:
    """Chat completion choice."""
    index: int
    message: ChatMessage
    finish_reason: Optional[str]

    def __init__(self, index: int, message: ChatMessage, finish_reason: Optional[str] = None):
        self.index = index
        self.message = message
        self.finish_reason = finish_reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "message": self.message.to_dict(),
            "finish_reason": self.finish_reason
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatChoice":
        message = ChatMessage.from_dict(data["message"])
        return cls(
            index=data["index"],
            message=message,
            finish_reason=data.get("finish_reason")
        )

class ChatUsage:
    """Usage statistics for chat completion."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

    def __init__(self, prompt_tokens: int, completion_tokens: int, total_tokens: int):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatUsage":
        return cls(
            prompt_tokens=data["prompt_tokens"],
            completion_tokens=data["completion_tokens"],
            total_tokens=data["total_tokens"]
        )

class ChatCompletionResponse:
    """Response object for chat completion."""
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatChoice]
    usage: ChatUsage

    def __init__(self, id: str, object: str, created: int, model: str, 
                 choices: List[ChatChoice], usage: ChatUsage):
        self.id = id
        self.object = object
        self.created = created
        self.model = model
        self.choices = choices
        self.usage = usage

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "object": self.object,
            "created": self.created,
            "model": self.model,
            "choices": [choice.to_dict() for choice in self.choices],
            "usage": self.usage.to_dict()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatCompletionResponse":
        choices = [ChatChoice.from_dict(choice) for choice in data["choices"]]
        usage = ChatUsage.from_dict(data["usage"])
        return cls(
            id=data["id"],
            object=data["object"],
            created=data["created"],
            model=data["model"],
            choices=choices,
            usage=usage
        )

class ChatCompletionChunk:
    """Streaming chat completion chunk."""
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Optional[ChatUsage] = None
    stream_summary: Optional[Dict[str, Any]] = None

    def __init__(self, id: str, object: str, created: int, model: str, choices: List[Dict[str, Any]], 
                 usage: Optional[ChatUsage] = None, stream_summary: Optional[Dict[str, Any]] = None):
        self.id = id
        self.object = object
        self.created = created
        self.model = model
        self.choices = choices
        self.usage = usage
        self.stream_summary = stream_summary

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "object": self.object,
            "created": self.created,
            "model": self.model,
            "choices": self.choices
        }
        if self.usage:
            result["usage"] = self.usage.to_dict()
        if self.stream_summary:
            result["stream_summary"] = self.stream_summary
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatCompletionChunk":
        usage = None
        if "usage" in data and data["usage"]:
            usage = ChatUsage.from_dict(data["usage"])
            
        return cls(
            id=data.get("id", ""),
            object=data.get("object", "chat.completion.chunk"),
            created=data.get("created", 0),
            model=data.get("model", ""),
            choices=data.get("choices", []),
            usage=usage,
            stream_summary=data.get("stream_summary")
        )
    
class CompletionChunk:
    """Streaming completion chunk."""
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Optional[ChatUsage] = None

    def __init__(self, id: str, object: str, created: int, model: str, choices: List[Dict[str, Any]], 
                 usage: Optional[ChatUsage] = None):
        self.id = id
        self.object = object
        self.created = created
        self.model = model
        self.choices = choices
        self.usage = usage

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "object": self.object,
            "created": self.created,
            "model": self.model,
            "choices": self.choices
        }
        if self.usage:
            result["usage"] = self.usage.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompletionChunk":
        usage = None
        if "usage" in data and data["usage"]:
            usage = ChatUsage.from_dict(data["usage"])
            
        return cls(
            id=data.get("id", ""),
            object=data.get("object", "completion.chunk"),
            created=data.get("created", 0),
            model=data.get("model", ""),
            choices=data.get("choices", []),
            usage=usage,
        )

class AudioTranscriptionResponse:
    """Response object for audio transcription."""
    text: str

    def __init__(self, text: str):
        self.text = text

    def to_dict(self) -> Dict[str, Any]:
        return {"text": self.text}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AudioTranscriptionResponse":
        return cls(text=data["text"])

class AudioTranslationResponse:
    """Response object for audio translation."""
    text: str

    def __init__(self, text: str):
        self.text = text

    def to_dict(self) -> Dict[str, Any]:
        return {"text": self.text}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AudioTranslationResponse":
        return cls(text=data["text"])

class RerankDocument:
    """Document for reranking."""
    index: int
    relevance_score: float
    document: Union[str, Dict[str, Any]]

    def __init__(self, index: int, relevance_score: float, document: Union[str, Dict[str, Any]]):
        self.index = index
        self.relevance_score = relevance_score
        self.document = document

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "relevance_score": self.relevance_score,
            "document": self.document
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RerankDocument":
        return cls(
            index=data["index"],
            relevance_score=data["relevance_score"],
            document=data["document"]
        )

class RerankResponse:
    """Response object for document reranking."""
    id: str
    results: List[RerankDocument]
    meta: Optional[Dict[str, Any]] = None

    def __init__(self, id: str, results: List[RerankDocument], meta: Optional[Dict[str, Any]] = None):
        self.id = id
        self.results = results
        self.meta = meta

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "results": [doc.to_dict() for doc in self.results]
        }
        if self.meta:
            result["meta"] = self.meta
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RerankResponse":
        results = [RerankDocument.from_dict(doc) for doc in data["results"]]
        return cls(
            id=data["id"],
            results=results,
            meta=data.get("meta")
        )

class CompletionChoice:
    """Text completion choice."""
    index: int
    text: str
    logprobs: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None
    stop_reason: Optional[str] = None
    prompt_logprobs: Optional[Dict[str, Any]] = None

    def __init__(self, index: int, text: str, logprobs: Optional[Dict[str, Any]] = None,
                 finish_reason: Optional[str] = None, stop_reason: Optional[str] = None,
                 prompt_logprobs: Optional[Dict[str, Any]] = None):
        self.index = index
        self.text = text
        self.logprobs = logprobs
        self.finish_reason = finish_reason
        self.stop_reason = stop_reason
        self.prompt_logprobs = prompt_logprobs

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "index": self.index,
            "text": self.text
        }
        if self.logprobs is not None:
            result["logprobs"] = self.logprobs
        if self.finish_reason is not None:
            result["finish_reason"] = self.finish_reason
        if self.stop_reason is not None:
            result["stop_reason"] = self.stop_reason
        if self.prompt_logprobs is not None:
            result["prompt_logprobs"] = self.prompt_logprobs
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompletionChoice":
        return cls(
            index=data["index"],
            text=data["text"],
            logprobs=data.get("logprobs"),
            finish_reason=data.get("finish_reason"),
            stop_reason=data.get("stop_reason"),
            prompt_logprobs=data.get("prompt_logprobs")
        )

class CompletionUsage:
    """Usage statistics for text completion."""
    prompt_tokens: int
    total_tokens: int
    completion_tokens: int

    def __init__(self, prompt_tokens: int, total_tokens: int, completion_tokens: int):
        self.prompt_tokens = prompt_tokens
        self.total_tokens = total_tokens
        self.completion_tokens = completion_tokens

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "total_tokens": self.total_tokens,
            "completion_tokens": self.completion_tokens
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompletionUsage":
        return cls(
            prompt_tokens=data["prompt_tokens"],
            total_tokens=data["total_tokens"],
            completion_tokens=data["completion_tokens"]
        )

class CompletionResponse:
    """Response object for text completion."""
    id: str
    object: str
    created: int
    model: str
    choices: List[CompletionChoice]
    usage: CompletionUsage

    def __init__(self, id: str, object: str, created: int, model: str, 
                 choices: List[CompletionChoice], usage: CompletionUsage):
        self.id = id
        self.object = object
        self.created = created
        self.model = model
        self.choices = choices
        self.usage = usage

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "object": self.object,
            "created": self.created,
            "model": self.model,
            "choices": [choice.to_dict() for choice in self.choices],
            "usage": self.usage.to_dict()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompletionResponse":
        choices = [CompletionChoice.from_dict(choice) for choice in data["choices"]]
        usage = CompletionUsage.from_dict(data["usage"])
        return cls(
            id=data["id"],
            object=data["object"],
            created=data["created"],
            model=data["model"],
            choices=choices,
            usage=usage
        )

class APIError:
    """API error response."""
    error: str
    details: Optional[Union[str, Dict[str, Any]]] = None
    status_code: Optional[int] = None

    def __init__(self, error: str, details: Optional[Union[str, Dict[str, Any]]] = None, 
                 status_code: Optional[int] = None):
        self.error = error
        self.details = details
        self.status_code = status_code

    def to_dict(self) -> Dict[str, Any]:
        result = {"error": self.error}
        if self.details is not None:
            result["details"] = self.details
        if self.status_code is not None:
            result["status_code"] = self.status_code
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "APIError":
        return cls(
            error=data["error"],
            details=data.get("details"),
            status_code=data.get("status_code")
        )

    def __str__(self) -> str:
        if self.details:
            return f"API Error: {self.error} - {self.details}"
        return f"API Error: {self.error}"
