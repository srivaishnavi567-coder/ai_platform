from typing import Any, Dict, List, Optional,Any

class FileObject:
    type: str
    transfer_method: str
    url: Optional[str] = None
    upload_file_id: Optional[str] = None

    def __init__(self, type: str, transfer_method: str, url: Optional[str] = None, upload_file_id: Optional[str] = None):
        self.type = type
        self.transfer_method = transfer_method
        self.url = url
        self.upload_file_id = upload_file_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "transfer_method": self.transfer_method,
            "url": self.url,
            "upload_file_id": self.upload_file_id
        }

class RetrieverResource:
    position: int
    dataset_id: str
    dataset_name: str
    document_id: str
    document_name: str
    segment_id: str
    score: float
    content: str

    def __init__(self, position: int, dataset_id: str, dataset_name: str, document_id: str,
                 document_name: str, segment_id: str, score: float, content: str):
        self.position = position
        self.dataset_id = dataset_id
        self.dataset_name = dataset_name
        self.document_id = document_id
        self.document_name = document_name
        self.segment_id = segment_id
        self.score = score
        self.content = content

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": self.position,
            "dataset_id": self.dataset_id,
            "dataset_name": self.dataset_name,
            "document_id": self.document_id,
            "document_name": self.document_name,
            "segment_id": self.segment_id,
            "score": self.score,
            "content": self.content
        }
    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'RetrieverResource':
        return cls(**d)

class MessageFile:
    id: str
    type: str
    url: str
    belongs_to: str

    def __init__(self, id: str, type: str, url: str, belongs_to: str):
        self.id = id
        self.type = type
        self.url = url
        self.belongs_to = belongs_to

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "url": self.url,
            "belongs_to": self.belongs_to
        }

class AgentThought:
    id: str
    message_id: str
    position: int
    thought: str
    tool: str
    tool_input: str
    observation: str
    created_at: int
    message_files: List[str]

    def __init__(self, id: str, message_id: str, position: int, thought: str, tool: str,
                 tool_input: str, observation: str, created_at: int, message_files: List[str]):
        self.id = id
        self.message_id = message_id
        self.position = position
        self.thought = thought
        self.tool = tool
        self.tool_input = tool_input
        self.observation = observation
        self.created_at = created_at
        self.message_files = message_files

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "message_id": self.message_id,
            "position": self.position,
            "thought": self.thought,
            "tool": self.tool,
            "tool_input": self.tool_input,
            "observation": self.observation,
            "created_at": self.created_at,
            "message_files": self.message_files
        }

class Message:
    id: str
    conversation_id: str
    inputs: Dict[str, Any]
    query: str
    answer: str
    message_files: List[MessageFile]
    feedback: Dict[str, Any]
    retriever_resources: List[RetrieverResource]
    agent_thoughts: List[AgentThought]
    created_at: int

    def __init__(self, id: str, conversation_id: str, inputs: Dict[str, Any], query: str, answer: str,
                 message_files: List[MessageFile], feedback: Dict[str, Any], retriever_resources: List[RetrieverResource],
                 agent_thoughts: List[AgentThought], created_at: int):
        self.id = id
        self.conversation_id = conversation_id
        self.inputs = inputs
        self.query = query
        self.answer = answer
        self.message_files = message_files
        self.feedback = feedback
        self.retriever_resources = retriever_resources
        self.agent_thoughts = agent_thoughts
        self.created_at = created_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "inputs": self.inputs,
            "query": self.query,
            "answer": self.answer,
            "message_files": [mf.to_dict() for mf in self.message_files],
            "feedback": self.feedback,
            "retriever_resources": [rr.to_dict() for rr in self.retriever_resources],
            "agent_thoughts": [at.to_dict() for at in self.agent_thoughts],
            "created_at": self.created_at
        }

class Conversation:
    id: str
    name: str
    inputs: Dict[str, Any]
    introduction: str
    created_at: int
    status: str

    def __init__(self, id: str, name: str, inputs: Dict[str, Any], introduction: str, created_at: int, status: str):
        self.id = id
        self.name = name
        self.inputs = inputs
        self.introduction = introduction
        self.created_at = created_at
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "inputs": self.inputs,
            "introduction": self.introduction,
            "created_at": self.created_at,
            "status": self.status
        }


class ChatMetaUsage:
    def __init__(self, prompt_tokens: int, prompt_unit_price: float, prompt_price: float, prompt_price_unit: str,
                 completion_tokens: int, completion_unit_price: float, completion_price: float, completion_price_unit: str,
                 total_tokens: int, total_price: float, currency: str, latency: float):
        self.prompt_tokens = prompt_tokens
        self.prompt_unit_price = prompt_unit_price
        self.prompt_price = prompt_price
        self.prompt_price_unit = prompt_price_unit
        self.completion_tokens = completion_tokens
        self.completion_unit_price = completion_unit_price
        self.completion_price = completion_price
        self.completion_price_unit = completion_price_unit
        self.total_tokens = total_tokens
        self.total_price = total_price
        self.currency = currency
        self.latency = latency

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "prompt_unit_price": self.prompt_unit_price,
            "prompt_price": self.prompt_price,
            "prompt_price_unit": self.prompt_price_unit,
            "completion_tokens": self.completion_tokens,
            "completion_unit_price": self.completion_unit_price,
            "completion_price": self.completion_price,
            "completion_price_unit": self.completion_price_unit,
            "total_tokens": self.total_tokens,
            "total_price": self.total_price,
            "currency": self.currency,
            "latency": self.latency
        }
    
    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'ChatMetaUsage':
        return cls(**d)


class ChatMetaData:
    def __init__(self, usage: ChatMetaUsage, retriever_resources: List[RetrieverResource]):
        self.usage = usage
        self.retriever_resources = retriever_resources

    def to_dict(self) -> Dict[str, Any]:
        return {
            "usage": self.usage.to_dict(),
            "retriever_resources": [r.to_dict() for r in self.retriever_resources]
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'ChatMetaData':
        # Handle usage safely
        usage_dict = d.get("usage", {})
        if isinstance(usage_dict, dict) and usage_dict:
            try:
                usage = ChatMetaUsage.from_dict(usage_dict)
            except (KeyError, TypeError):
                # Create default usage if parsing fails
                usage = ChatMetaUsage(0, 0.0, 0.0, "INR", 0, 0.0, 0.0, "INR", 0, 0.0, "INR", 0.0)
        else:
            # Create default usage if not present
            usage = ChatMetaUsage(0, 0.0, 0.0, "INR", 0, 0.0, 0.0, "INR", 0, 0.0, "INR", 0.0)

        # Handle retriever_resources safely
        resources_list = d.get("retriever_resources", [])
        retriever_resources = []
        if isinstance(resources_list, list):
            for r in resources_list:
                try:
                    retriever_resources.append(RetrieverResource.from_dict(r))
                except (KeyError, TypeError):
                    continue

        return cls(usage=usage, retriever_resources=retriever_resources)


class ChatCompletionResponse:
    def __init__(self, event: str, message_id: str, conversation_id: str, mode: str,
                 answer: str, metadata: ChatMetaData, created_at: int, id: Optional[str] = None,
                 task_id: Optional[str] = None):
        self.id = id
        self.event = event
        self.message_id = message_id
        self.conversation_id = conversation_id
        self.mode = mode
        self.answer = answer
        self.metadata = metadata
        self.created_at = created_at
        self.task_id = task_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "event": self.event,
            "message_id": self.message_id,
            "conversation_id": self.conversation_id,
            "mode": self.mode,
            "answer": self.answer,
            "metadata": self.metadata.to_dict(),
            "created_at": self.created_at,
            "task_id": self.task_id
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'ChatCompletionResponse':
        # Handle metadata safely - create default if missing or malformed
        metadata_dict = d.get("metadata", {})
        if isinstance(metadata_dict, dict) and "usage" in metadata_dict:
            try:
                metadata = ChatMetaData.from_dict(metadata_dict)
            except (KeyError, TypeError):
                # Create default metadata if parsing fails
                default_usage = ChatMetaUsage(0, 0.0, 0.0, "INR", 0, 0.0, 0.0, "INR", 0, 0.0, "INR", 0.0)
                metadata = ChatMetaData(usage=default_usage, retriever_resources=[])
        else:
            # Create default metadata if not present
            default_usage = ChatMetaUsage(0, 0.0, 0.0, "INR", 0, 0.0, 0.0, "INR", 0, 0.0, "INR", 0.0)
            metadata = ChatMetaData(usage=default_usage, retriever_resources=[])

        return cls(
            id=d.get("id"),
            event=d.get("event", "message"),
            message_id=d.get("message_id", ""),
            conversation_id=d.get("conversation_id", ""),
            mode=d.get("mode", "chat"),
            answer=d.get("answer", ""),
            metadata=metadata,
            created_at=d.get("created_at", 0),
            task_id=d.get("task_id")
        )
    
class ChatCompletionStreamResponse:
    def __init__(self, event: str, message_id: str = None, task_id: str = None, conversation_id: str = None, answer: str = None, created_at: int = None, metadata: dict = None, id: str = None):
        self.event = event
        self.task_id = task_id
        self.message_id = message_id
        self.conversation_id = conversation_id
        self.answer = answer
        self.created_at = created_at
        self.metadata = metadata
        self.id = id

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'ChatCompletionStreamResponse':
        return cls(
            event=d.get("event"),
            task_id=d.get("task_id"),
            message_id=d.get("message_id"),
            conversation_id=d.get("conversation_id"),
            answer=d.get("answer"),
            created_at=d.get("created_at"),
            metadata=d.get("metadata"),
            id=d.get("id")
        )

class PreProcessingRule:
    id: str
    enabled: bool

    def __init__(self, id: str, enabled: bool):
        self.id = id
        self.enabled = enabled

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "enabled": self.enabled
        }

class SegmentationRule:
    separator: str
    max_tokens: int

    def __init__(self, separator: str, max_tokens: int):
        self.separator = separator
        self.max_tokens = max_tokens

    def to_dict(self) -> Dict[str, Any]:
        return {
            "separator": self.separator,
            "max_tokens": self.max_tokens
        }

class ProcessRule:
    mode: str
    rules: Optional[Dict[str, Any]] = None

    def __init__(self, mode: str, rules: Optional[Dict[str, Any]] = None):
        self.mode = mode
        self.rules = rules

    def to_dict(self) -> Dict[str, Any]:
        result = {"mode": self.mode}
        if self.rules:
            result["rules"] = {
                "pre_processing_rules": [rule.to_dict() for rule in self.rules.get("pre_processing_rules", [])],
                "segmentation": self.rules["segmentation"].to_dict() if self.rules.get("segmentation") else {}
            }
        return result

class Dataset:
    id: str
    name: str
    description: Optional[str] = None
    provider: str
    permission: str
    data_source_type: Optional[str] = None
    indexing_technique: Optional[str] = None
    app_count: int
    document_count: int
    word_count: int
    created_by: str
    created_at: int
    updated_by: str
    updated_at: int
    embedding_model: Optional[str] = None
    embedding_model_provider: Optional[str] = None
    embedding_available: Optional[bool] = None
    retrieval_model_dict: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

    def __init__(self, id: str, name: str, description: Optional[str], provider: str, permission: str,
                 data_source_type: Optional[str], indexing_technique: Optional[str], app_count: int,
                 document_count: int, word_count: int, created_by: str, created_at: int,
                 updated_by: str, updated_at: int, embedding_model: Optional[str],
                 embedding_model_provider: Optional[str], embedding_available: Optional[bool],
                 retrieval_model_dict: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None):
        self.id = id
        self.name = name
        self.description = description
        self.provider = provider
        self.permission = permission
        self.data_source_type = data_source_type
        self.indexing_technique = indexing_technique
        self.app_count = app_count
        self.document_count = document_count
        self.word_count = word_count
        self.created_by = created_by
        self.created_at = created_at
        self.updated_by = updated_by
        self.updated_at = updated_at
        self.embedding_model = embedding_model
        self.embedding_model_provider = embedding_model_provider
        self.embedding_available = embedding_available
        self.retrieval_model_dict = retrieval_model_dict
        self.tags = tags

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "provider": self.provider,
            "permission": self.permission,
            "data_source_type": self.data_source_type,
            "indexing_technique": self.indexing_technique,
            "app_count": self.app_count,
            "document_count": self.document_count,
            "word_count": self.word_count,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "updated_by": self.updated_by,
            "updated_at": self.updated_at,
            "embedding_model": self.embedding_model,
            "embedding_model_provider": self.embedding_model_provider,
            "embedding_available": self.embedding_available,
            "retrieval_model_dict": self.retrieval_model_dict,
            "tags": self.tags
        }

class BatchStatus:
    id: str
    indexing_status: str
    processing_started_at: float
    parsing_completed_at: Optional[float] = None
    cleaning_completed_at: Optional[float] = None
    splitting_completed_at: Optional[float] = None
    completed_at: Optional[float] = None
    paused_at: Optional[float] = None
    error: Optional[str] = None
    stopped_at: Optional[float] = None
    completed_segments: int
    total_segments: int

    def __init__(self, id: str, indexing_status: str, processing_started_at: float,
                 parsing_completed_at: Optional[float], cleaning_completed_at: Optional[float],
                 splitting_completed_at: Optional[float], completed_at: Optional[float],
                 paused_at: Optional[float], error: Optional[str], stopped_at: Optional[float],
                 completed_segments: int, total_segments: int):
        self.id = id
        self.indexing_status = indexing_status
        self.processing_started_at = processing_started_at
        self.parsing_completed_at = parsing_completed_at
        self.cleaning_completed_at = cleaning_completed_at
        self.splitting_completed_at = splitting_completed_at
        self.completed_at = completed_at
        self.paused_at = paused_at
        self.error = error
        self.stopped_at = stopped_at
        self.completed_segments = completed_segments
        self.total_segments = total_segments

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "indexing_status": self.indexing_status,
            "processing_started_at": self.processing_started_at,
            "parsing_completed_at": self.parsing_completed_at,
            "cleaning_completed_at": self.cleaning_completed_at,
            "splitting_completed_at": self.splitting_completed_at,
            "completed_at": self.completed_at,
            "paused_at": self.paused_at,
            "error": self.error,
            "stopped_at": self.stopped_at,
            "completed_segments": self.completed_segments,
            "total_segments": self.total_segments
        }

class Document:
    id: str
    position: int
    data_source_type: str
    data_source_info: Dict[str, Any]
    dataset_process_rule_id: str
    name: str
    created_from: str
    created_by: str
    created_at: int
    tokens: int
    indexing_status: str
    error: Optional[str] = None
    enabled: bool
    disabled_at: Optional[int] = None
    disabled_by: Optional[str] = None
    archived: bool
    display_status: str
    word_count: int
    hit_count: int
    doc_form: str
    data_source_detail_dict: Optional[Dict[str, Any]] = None

    def __init__(self, id: str, position: int, data_source_type: str, data_source_info: Dict[str, Any],
                 dataset_process_rule_id: str, name: str, created_from: str, created_by: str,
                 created_at: int, tokens: int, indexing_status: str, error: Optional[str],
                 enabled: bool, disabled_at: Optional[int], disabled_by: Optional[str],
                 archived: bool, display_status: str, word_count: int, hit_count: int, doc_form: str,
                 data_source_detail_dict: Optional[Dict[str, Any]] = None):
        self.id = id
        self.position = position
        self.data_source_type = data_source_type
        self.data_source_info = data_source_info
        self.dataset_process_rule_id = dataset_process_rule_id
        self.name = name
        self.created_from = created_from
        self.created_by = created_by
        self.created_at = created_at
        self.tokens = tokens
        self.indexing_status = indexing_status
        self.error = error
        self.enabled = enabled
        self.disabled_at = disabled_at
        self.disabled_by = disabled_by
        self.archived = archived
        self.display_status = display_status
        self.word_count = word_count
        self.hit_count = hit_count
        self.doc_form = doc_form
        self.data_source_detail_dict = data_source_detail_dict

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "position": self.position,
            "data_source_type": self.data_source_type,
            "data_source_info": self.data_source_info,
            "dataset_process_rule_id": self.dataset_process_rule_id,
            "name": self.name,
            "created_from": self.created_from,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "tokens": self.tokens,
            "indexing_status": self.indexing_status,
            "error": self.error,
            "enabled": self.enabled,
            "disabled_at": self.disabled_at,
            "disabled_by": self.disabled_by,
            "archived": self.archived,
            "display_status": self.display_status,
            "word_count": self.word_count,
            "hit_count": self.hit_count,
            "doc_form": self.doc_form,
            "data_source_detail_dict": self.data_source_detail_dict
        }

class DocumentResponse:
    document: Document
    batch: str

    def __init__(self, document: Document, batch: str):
        self.document = document
        self.batch = batch

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document": self.document.to_dict(),
            "batch": self.batch
        }

class DatasetResponse:
    id: str
    name: str
    description: Optional[str] = None
    provider: str
    permission: str
    data_source_type: Optional[str] = None
    indexing_technique: Optional[str] = None
    app_count: int
    document_count: int
    word_count: int
    created_by: str
    created_at: int
    updated_by: str
    updated_at: int
    embedding_model: Optional[str] = None
    embedding_model_provider: Optional[str] = None
    embedding_available: Optional[bool] = None
    retrieval_model_dict: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

    def __init__(self, id: str, name: str, description: Optional[str], provider: str, permission: str,
                 data_source_type: Optional[str], indexing_technique: Optional[str], app_count: int,
                 document_count: int, word_count: int, created_by: str, created_at: int,
                 updated_by: str, updated_at: int, embedding_model: Optional[str],
                 embedding_model_provider: Optional[str], embedding_available: Optional[bool],
                 retrieval_model_dict: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None):
        self.id = id
        self.name = name
        self.description = description
        self.provider = provider
        self.permission = permission
        self.data_source_type = data_source_type
        self.indexing_technique = indexing_technique
        self.app_count = app_count
        self.document_count = document_count
        self.word_count = word_count
        self.created_by = created_by
        self.created_at = created_at
        self.updated_by = updated_by
        self.updated_at = updated_at
        self.embedding_model = embedding_model
        self.embedding_model_provider = embedding_model_provider
        self.embedding_available = embedding_available
        self.retrieval_model_dict = retrieval_model_dict
        self.tags = tags

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "provider": self.provider,
            "permission": self.permission,
            "data_source_type": self.data_source_type,
            "indexing_technique": self.indexing_technique,
            "app_count": self.app_count,
            "document_count": self.document_count,
            "word_count": self.word_count,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "updated_by": self.updated_by,
            "updated_at": self.updated_at,
            "embedding_model": self.embedding_model,
            "embedding_model_provider": self.embedding_model_provider,
            "embedding_available": self.embedding_available,
            "retrieval_model_dict": self.retrieval_model_dict,
            "tags": self.tags
        }

class ListKnowledgeResponse:
    data: List[Dataset]
    has_more: bool
    limit: int
    total: int
    page: int

    def __init__(self, data: List[Dataset], has_more: bool, limit: int, total: int, page: int):
        self.data = data
        self.has_more = has_more
        self.limit = limit
        self.total = total
        self.page = page

    def to_dict(self) -> Dict[str, Any]:
        return {
            "data": [dataset.to_dict() for dataset in self.data],
            "has_more": self.has_more,
            "limit": self.limit,
            "total": self.total,
            "page": self.page
        }

class ListDocumentsResponse:
    data: List[Document]
    has_more: bool
    limit: int
    total: int
    page: int

    def __init__(self, data: List[Document], has_more: bool, limit: int, total: int, page: int):
        self.data = data
        self.has_more = has_more
        self.limit = limit
        self.total = total
        self.page = page

    def to_dict(self) -> Dict[str, Any]:
        return {
            "data": [doc.to_dict() for doc in self.data],
            "has_more": self.has_more,
            "limit": self.limit,
            "total": self.total,
            "page": self.page
        }

class BatchStatusResponse:
    data: List[BatchStatus]

    def __init__(self, data: List[BatchStatus]):
        self.data = data

    def to_dict(self) -> Dict[str, Any]:
        return {
            "data": [status.to_dict() for status in self.data]
        }

class DeleteResponse:
    status: str

    def __init__(self, status: str):
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status
        }


class FileUploadResponse:
    id: str
    name: str
    size: int
    extension: str
    mime_type: str
    created_by: str
    created_at: int

    def __init__(self, id: str, name: str, size: int, extension: str, 
                 mime_type: str, created_by: str, created_at: int):
        self.id = id
        self.name = name
        self.size = size
        self.extension = extension
        self.mime_type = mime_type
        self.created_by = created_by
        self.created_at = created_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "size": self.size,
            "extension": self.extension,
            "mime_type": self.mime_type,
            "created_by": self.created_by,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'FileUploadResponse':
        return cls(
            id=d["id"],
            name=d["name"],
            size=d["size"],
            extension=d["extension"],
            mime_type=d["mime_type"],
            created_by=d["created_by"],
            created_at=d["created_at"]
        )

