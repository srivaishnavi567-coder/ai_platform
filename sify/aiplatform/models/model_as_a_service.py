import json
import requests
from typing import Any, Dict, Generator, List, Optional, Union, BinaryIO

from sify.aiplatform.models.types import (
    ModelsListResponse, 
    EmbeddingResponse,
    ChatCompletionResponse, 
    ChatCompletionChunk,
    CompletionResponse,
    CompletionChunk,
    AudioTranscriptionResponse,
    AudioTranslationResponse,
    RerankResponse,
    APIError
)
# new lines for langfuse patching
# 




class ModelAsAService:
    def __init__(self, api_key: str, model_id: str = None):
        
        if not api_key or not api_key.strip():
            raise ValueError("API key must be provided and cannot be empty")

        self.base_url = "https://infinitai.sifymdp.digital/maas"
        self.api_key = api_key.strip()
        self.model_id = model_id.strip() if model_id else None

    def _send_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        form_data: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        return_binary: bool = False
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None], bytes]:
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Set content type appropriately
        if not files and not form_data:
            headers["Content-Type"] = "application/json"

        try:
            # Prepare request arguments
            request_kwargs = {
                "method": method,
                "url": url,
                "headers": headers,
                "stream": stream,
                "timeout": 300
            }

            # Add data based on request type
            if files:
                request_kwargs["files"] = files
                if form_data:
                    request_kwargs["data"] = form_data
            elif form_data:
                request_kwargs["data"] = form_data
            elif json_data:
                request_kwargs["json"] = json_data

            if params:
                request_kwargs["params"] = params

            response = requests.request(**request_kwargs)

            # Handle error status codes
            if response.status_code >= 400:
                error_msg = "Request failed"
                error_details = None
                
                try:
                    error_response = response.json()
                    if isinstance(error_response, dict):
                        if 'error' in error_response:
                            error_msg = error_response['error']
                            error_details = error_response.get('details')
                        elif 'message' in error_response:
                            error_msg = error_response['message']
                        elif 'detail' in error_response:
                            error_msg = error_response['detail']
                    else:
                        error_msg = str(error_response)
                except json.JSONDecodeError:
                    error_msg = response.text if response.text else f"HTTP {response.status_code} Error"
                
                # Handle specific error codes
                if response.status_code == 403:
                    error_msg = f"Forbidden: API key is not subscribed for model '{self.model_id}' or access denied"
                elif response.status_code == 401:
                    error_msg = "Unauthorized: Invalid API key"
                elif response.status_code == 404:
                    error_msg = f"Not Found: Model '{self.model_id}' not found or endpoint not available"
                elif response.status_code == 429:
                    error_msg = "Rate limit exceeded: Too many requests"
                elif response.status_code >= 500:
                    error_msg = f"Server error: HTTP {response.status_code}"
  
                api_error = APIError(
                    error=error_msg,
                    details=error_details,
                    status_code=response.status_code
                )
                raise ValueError(str(api_error))

            # Handle streaming responses
            if stream:
                return self._handle_stream_response(response)

            # Handle binary responses (e.g., audio files)
            if return_binary or self._is_binary_response(response):
                return response.content

            # Handle JSON responses
            if response.content:
                try:
                    result = response.json()
                    return {"status_code": response.status_code, "result": result}
                except json.JSONDecodeError:
                    # If we can't parse JSON but expected it, check if it's HTML or other format
                    content_type = response.headers.get('Content-Type', '')
                    if 'text/html' in content_type:
                        raise ValueError(f"Received HTML response instead of JSON: {response.text[:200]}")
                    elif 'text/plain' in content_type:
                        raise ValueError(f"Received plain text response: {response.text}")
                    else:
                        raise ValueError(f"Failed to parse JSON response: {response.text[:200]}")
            else:
                return {"status_code": response.status_code, "result": {}}

        except requests.RequestException as e:
            error_msg = str(e).lower()
            if "timeout" in error_msg:
                raise ValueError("Request timeout - the API took too long to respond")
            elif "connection" in error_msg:
                raise ValueError("Connection error - unable to reach the API")
            elif "ssl" in error_msg:
                raise ValueError("SSL/TLS error - certificate verification failed")
            else:
                raise ValueError(f"Request failed: {str(e)}")

    def _handle_stream_response(self, response) -> Generator[Dict[str, Any], None, None]:
        try:
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    # Handle server-sent events format
                    if line.startswith("data: "):
                        data_str = line[len("data: "):].strip()
                        if data_str and data_str != "[DONE]":
                            try:
                                chunk_data = json.loads(data_str)
                                yield chunk_data
                            except json.JSONDecodeError:
                                # Skip malformed JSON chunks
                                continue
                    # Handle raw JSON lines
                    elif line.strip():
                        try:
                            chunk_data = json.loads(line.strip())
                            yield chunk_data
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            raise ValueError(f"Error processing stream: {str(e)}")

    def _is_binary_response(self, response) -> bool:
        content_type = response.headers.get("Content-Type", "").lower()
        return (
            content_type.startswith("audio/") or
            content_type.startswith("video/") or
            content_type.startswith("image/") or
            content_type == "application/octet-stream" or
            "binary" in content_type
        )
    

    def _validate_required_params(self, params: Dict[str, Any]) -> None:
        """
        Validate that required parameters are not empty or None.
        
        Args:
            params (Dict[str, Any]): Dictionary of parameter names and values to validate
            
        Raises:
            ValueError: If any required parameter is empty, None, or invalid
        """
        for param_name, param_value in params.items():
            if param_value is None:
                raise ValueError(f"{param_name} must not be None")
            if isinstance(param_value, str) and not param_value.strip():
                raise ValueError(f"{param_name} must not be empty or whitespace")
            if isinstance(param_value, (list, dict)) and not param_value:
                raise ValueError(f"{param_name} must not be empty")
            if isinstance(param_value, (int, float)) and param_value < 0:
                raise ValueError(f"{param_name} must not be negative")
    
    def _validate_optional_params(self, params: Dict[str, Any]) -> None:
        """
        Validate optional parameters if they are provided.
        
        Args:
            params (Dict[str, Any]): Dictionary of parameter names and values to validate
            
        Raises:
            ValueError: If any optional parameter has invalid value
        """
        for param_name, param_value in params.items():
            if param_value is not None:
                if isinstance(param_value, str) and not param_value.strip():
                    raise ValueError(f"{param_name} must not be empty or whitespace")
                if isinstance(param_value, (int, float)) and param_value < 0:
                    raise ValueError(f"{param_name} must not be negative")

    # Audio Service Methods
    def speech_to_text(self, file: BinaryIO, **kwargs) -> AudioTranscriptionResponse:
        """
        Transcribe audio file to text using speech-to-text models.

        Args:
            file (BinaryIO): Audio file to transcribe (supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm)
            **kwargs: Additional parameters:
                - language (str): Language of the input audio (ISO-639-1 format, e.g., "en")
                - prompt (str): Optional text to guide the model's style or continue a previous audio segment
                - response_format (str): Format of the transcript output ("json", "text", "srt", "verbose_json", "vtt")
                - temperature (float): Sampling temperature between 0 and 1

        Returns:
            AudioTranscriptionResponse: Object containing:
                - text (str): The transcribed text

        Raises:
            ValueError: If file is missing, or if the API request fails
        """
        if file is None:
            raise ValueError("File must be provided")
        self._validate_optional_params(kwargs)

        if self.model_id is None:
            raise ValueError("Model ID must is not set for this instance")
        
        form_data = {"model": self.model_id}
        form_data.update(kwargs)
        
        response = self._send_request(
            method="POST",
            endpoint="/v1/audio/transcriptions",
            files={"file": file},
            form_data=form_data
        )
        
        return AudioTranscriptionResponse.from_dict(response["result"])

    def audio_translation(self, file: BinaryIO, **kwargs) -> AudioTranslationResponse:
        """
        Translate audio file in other Languages to English text using speech-to-text models.

        Args:
            file (BinaryIO): Audio file to translate (supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm)
            **kwargs: Additional parameters:
                - prompt (str): Optional text to guide the model's style or continue a previous audio segment
                - response_format (str): Format of the transcript output ("json", "text", "srt", "verbose_json", "vtt")
                - temperature (float): Sampling temperature between 0 and 1

        Returns:
            AudioTranslationResponse: Object containing:
                - text (str): The translated text in English

        Raises:
            ValueError: If file is missing, or if the API request fails
        """
        if file is None:
            raise ValueError("File must be provided")
        self._validate_optional_params(kwargs)

        if self.model_id is None:
            raise ValueError("Model ID must is not set for this instance")
        
        form_data = {"model": self.model_id}
        form_data.update(kwargs)
        
        response = self._send_request(
            method="POST",
            endpoint="/v1/audio/translations",
            files={"file": file},
            form_data=form_data
        )

        return AudioTranslationResponse.from_dict(response["result"])

    def text_to_speech(self, input_text: str, voice: str, **kwargs) -> bytes:
        """
        Convert text to speech using text-to-speech models.

        Args:
            input_text (str): The text to convert to speech (maximum 4096 characters)
            voice (str): Voice to use for speech synthesis (e.g., "alloy", "echo", "fable", "onyx", "nova", "shimmer")
            **kwargs: Additional parameters:
                - response_format (str): Audio format ("mp3", "opus", "aac", "flac")
                - speed (float): Speed of generated audio (0.25 to 4.0)

        Returns:
            bytes: The generated audio file as binary data

        Raises:
            ValueError: If required parameters are missing or if the API request fails
        """
        self._validate_required_params({
            "input": input_text,
            "voice": voice
        })
        self._validate_optional_params(kwargs)

        if self.model_id is None:
            raise ValueError("Model ID must is not set for this instance")
        
        data = {
            "model": self.model_id,
            "input": input_text,
            "voice": voice
        }
        data.update(kwargs)
        
        return self._send_request(
            method="POST",
            endpoint="/v1/audio/speech",
            json_data=data,
            return_binary=True
        )
    
    # Embedding Service Methods
    def create_embeddings(self, input_data: Union[str, List[str]], **kwargs) -> EmbeddingResponse:
        """
        Create embeddings for input text using embedding models.

        Args:
            input_data (Union[str, List[str]]): Text string or list of text strings to embed
            **kwargs: Additional parameters:
                - encoding_format (str): Format to return embeddings ("float", "base64")
                - dimensions (int): Number of dimensions for the output embeddings (model-specific)
                - user (str): Unique identifier representing your end-user

        Returns:
            EmbeddingResponse: Object containing:
                - object (str): Type of object returned (always "list")
                - data (List[EmbeddingData]): List of embedding objects with:
                    - object (str): Type of object (always "embedding")
                    - embedding (List[float]): The embedding vector
                    - index (int): Index of the embedding in the input list
                - model (str): The model used for embedding
                - usage (EmbeddingUsage): Usage statistics with:
                    - prompt_tokens (int): Number of tokens in the input
                    - total_tokens (int): Total tokens processed

        Raises:
            ValueError: If required parameters are missing or if the API request fails
        """
        self._validate_required_params({"input": input_data})
        self._validate_optional_params(kwargs)
        
        # Validate input_data structure
        if isinstance(input_data, list):
            for i, item in enumerate(input_data):
                if not isinstance(item, str) or not item.strip():
                    raise ValueError(f"Input item {i} must be a non-empty string")
        elif not isinstance(input_data, str) or not input_data.strip():
            raise ValueError("Input data must be a non-empty string or list of non-empty strings")
        
        if self.model_id is None:
            raise ValueError("Model ID must is not set for this instance")
        
        data = {
            "model": self.model_id,
            "input": input_data
        }
        data.update(kwargs)
        
        response = self._send_request(
            method="POST",
            endpoint="/v1/embeddings",
            json_data=data
        )
        
        return EmbeddingResponse.from_dict(response["result"])

    # LLM Service Methods
    
    def chat_completion(self, messages: List[Dict[str, Any]], 
                       stream: bool = False, **kwargs) -> Union[ChatCompletionResponse, Generator[ChatCompletionChunk, None, None]]:
        """
        Create a chat completion using large language models.

        Args:
            messages (List[Dict[str, Any]]): List of messages in the conversation. Each message should have:
                - role (str): The role of the message author ("system", "user", "assistant")
                - content (str): The content of the message
            stream (bool): Whether to stream back partial message deltas. Defaults to False.
            **kwargs: Additional parameters:
                - temperature (float): Sampling temperature (0-2). Higher values make output more random
                - max_tokens (int): Maximum number of tokens to generate
                - top_p (float): Nucleus sampling parameter (0-1)
                - frequency_penalty (float): Penalty for repeated tokens (-2.0 to 2.0)
                - presence_penalty (float): Penalty for new topics (-2.0 to 2.0)
                - stop (Union[str, List[str]]): Sequences where the API will stop generating

        Returns:
            Union[ChatCompletionResponse, Generator]: 
                - If stream=False: ChatCompletionResponse object containing:
                    - id (str): Unique identifier for the completion
                    - object (str): Object type (always "chat.completion")
                    - created (int): Unix timestamp of creation
                    - model (str): Model used for completion
                    - choices (List[ChatChoice]): List of completion choices
                    - usage (ChatUsage): Token usage statistics
                - If stream=True: Generator yielding ChatCompletionChunk objects

        Raises:
            ValueError: If required parameters are missing or if the API request fails
        """
        self._validate_required_params({"messages": messages})
        self._validate_optional_params(kwargs)
        
        # Validate messages structure
        for i, message in enumerate(messages):
            if not isinstance(message, dict):
                raise ValueError(f"Message {i} must be a dictionary")
            if "role" not in message or not message["role"]:
                raise ValueError(f"Message {i} must have a valid 'role' field")
            if "content" not in message or not message["content"]:
                raise ValueError(f"Message {i} must have a valid 'content' field")
        
        if self.model_id is None:
            raise ValueError("Model ID must is not set for this instance")
        
        data = {
            "model": self.model_id,
            "messages": messages,
            "stream": stream
        }
        data.update(kwargs)
        
        def _non_stream_generator():
            response = self._send_request(
                method="POST",
                endpoint="/v1/chat/completions",
                json_data=data
            )
            return ChatCompletionResponse.from_dict(response["result"])   
        if stream:
            def _stream_generator():
                collected_text = ""
                model_name = self.model_id
                chunk_count = 0
                first_chunk_time = None
                last_chunk_time = None
                
                stream_generator = self._send_request(
                    method="POST",
                    endpoint="/v1/chat/completions",
                    json_data=data,
                    stream=True
                )
                
                for chunk_data in stream_generator:
                    if not chunk_data or not isinstance(chunk_data, dict):
                        continue
                        
                    chunk_count += 1
                    if first_chunk_time is None:
                        first_chunk_time = chunk_data.get("created", 0)
                    last_chunk_time = chunk_data.get("created", 0)
                    
                    # Extract content from chunk and accumulate
                    if "choices" in chunk_data and chunk_data["choices"]:
                        choice = chunk_data["choices"][0]
                        if "delta" in choice and "content" in choice["delta"]:
                            content = choice["delta"]["content"]
                            if content:
                                collected_text += content
                                
                    # Yield the chunk as-is for streaming
                    yield ChatCompletionChunk.from_dict(chunk_data)
                
                # After streaming is complete, yield a final summary chunk with usage info
                # if collected_text:
                #     # Estimate token usage
                #     prompt_text = " ".join([msg.get("content", "") for msg in messages])
                #     estimated_prompt_tokens = len(prompt_text.split())
                #     estimated_completion_tokens = len(collected_text.split())
                #     estimated_total_tokens = estimated_prompt_tokens + estimated_completion_tokens
                    
                #     # Create a final summary chunk
                #     summary_chunk = {
                #         "id": f"chatcmpl-{chunk_count}",
                #         "object": "chat.completion.chunk", 
                #         "created": last_chunk_time or 0,
                #         "model": model_name,
                #         "choices": [{
                #             "index": 0,
                #             "delta": {},
                #             "finish_reason": "stop"
                #         }],
                #         "usage": {
                #             "prompt_tokens": estimated_prompt_tokens,
                #             "completion_tokens": estimated_completion_tokens,
                #             "total_tokens": estimated_total_tokens
                #         },
                #         "stream_summary": {
                #             "collected_text": collected_text,
                #             "chunk_count": chunk_count,
                #             "model": model_name
                #         }
                #     }
                #     yield ChatCompletionChunk.from_dict(summary_chunk)
                    
            return _stream_generator()
        else:
            return _non_stream_generator()

            

    def completion(self, prompt: str, stream: bool = False, **kwargs) -> Union[CompletionResponse, Generator[CompletionChunk, None, None]]:
        """
        Create a text completion using large language models.

        Args:
            prompt (str): The prompt text to complete
            stream (bool): Whether to stream back partial completions. Defaults to False.
            **kwargs: Additional parameters:
                - temperature (float): Sampling temperature (0-2). Higher values make output more random
                - max_tokens (int): Maximum number of tokens to generate
                - top_p (float): Nucleus sampling parameter (0-1)
                - frequency_penalty (float): Penalty for repeated tokens (-2.0 to 2.0)
                - presence_penalty (float): Penalty for new topics (-2.0 to 2.0)
                - stop (Union[str, List[str]]): Sequences where the API will stop generating
                - echo (bool): Whether to echo back the prompt in the response

        Returns:
            Union[CompletionResponse, Generator]: 
                - If stream=False: CompletionResponse object containing:
                    - id (str): Unique identifier for the completion
                    - object (str): Object type (always "text_completion")
                    - created (int): Unix timestamp of creation
                    - model (str): Model used for completion
                    - choices (List[CompletionChoice]): List of completion choices
                    - usage (CompletionUsage): Token usage statistics
                - If stream=True: Generator yielding completion chunks

        Raises:
            ValueError: If required parameters are missing or if the API request fails
        """
        self._validate_required_params({"prompt": prompt})
        self._validate_optional_params(kwargs)
        
        if self.model_id is None:
            raise ValueError("Model ID must is not set for this instance")
        
        data = {
            "model": self.model_id,
            "prompt": prompt,
            "stream": stream
        }
        data.update(kwargs)

        def _non_stream_generator():
            response = self._send_request(
                method="POST",
                endpoint="/v1/completions",
                json_data=data
            )
            return CompletionResponse.from_dict(response["result"])
        if stream:
            def _stream_generator():
                collected_text = ""
                model_name = self.model_id
                chunk_count = 0
                first_chunk_time = None
                last_chunk_time = None

                stream_generator = self._send_request(
                    method="POST",
                    endpoint="/v1/completions",
                    json_data=data,
                    stream=True
                )

                for chunk_data in stream_generator:
                    if not chunk_data or not isinstance(chunk_data, dict):
                        continue
                        
                    chunk_count += 1
                    if first_chunk_time is None:
                        first_chunk_time = chunk_data.get("created", 0)
                    last_chunk_time = chunk_data.get("created", 0)
                    
                    # Extract content from chunk and accumulate
                    if "choices" in chunk_data and chunk_data["choices"]:
                        choice = chunk_data["choices"][0]
                        if "delta" in choice and "content" in choice["delta"]:
                            content = choice["delta"]["content"]
                            if content:
                                collected_text += content
                                
                    # Yield the chunk as-is for streaming
                    yield CompletionChunk.from_dict(chunk_data)

                # After streaming is complete, yield a final summary chunk with usage info
                # if collected_text:
                #     # Estimate token usage
                #     prompt_text = prompt
                #     estimated_prompt_tokens = len(prompt_text.split())
                #     estimated_completion_tokens = len(collected_text.split())
                #     estimated_total_tokens = estimated_prompt_tokens + estimated_completion_tokens
                    
                #     # Create a final summary chunk
                #     summary_chunk = {
                #         "id": f"cmpl-{chunk_count}",
                #         "object": "completion.chunk", 
                #         "created": last_chunk_time or 0,
                #         "model": model_name,
                #         "choices": [{
                #             "index": 0,
                #             "delta": {},
                #             "finish_reason": "stop"
                #         }],
                #         "usage": {
                #             "prompt_tokens": estimated_prompt_tokens,
                #             "completion_tokens": estimated_completion_tokens,
                #             "total_tokens": estimated_total_tokens
                #         },
                #         "stream_summary": {
                #             "collected_text": collected_text,
                #             "chunk_count": chunk_count,
                #             "model": model_name
                #         }
                #     }
                #     yield CompletionChunk.from_dict(summary_chunk)
            return _stream_generator()
        else:
            return _non_stream_generator()
             
    # Models Service Methods
    def list_models(self) -> ModelsListResponse:
        """
        List all available models on the server.

        Returns:
            ModelsListResponse: Object containing:
                - models (List[ModelInfo]): List of available models, each with:
                    - id (str): Unique model identifier
                    - name (str): Human-readable model name
                    - model_type (str): Type of model ("llm", "embedding", "audio", "rerank")
                    - max_tokens (Optional[int]): Maximum context length for the model
                    - dimensions (Optional[int]): Embedding dimensions (for embedding models)
                    - language (Optional[List[str]]): Supported languages

        Raises:
            ValueError: If the API request fails
        """
        response = self._send_request(
            method="GET",
            endpoint="/v1/models"
        )
        
        return ModelsListResponse.from_dict(response["result"])

    # Rerank Service Methods
    def rerank(self, query: str, documents: List[Union[str, Dict[str, Any]]], 
              **kwargs) -> RerankResponse:
        """
        Rerank documents based on their relevance to a query using reranking models.

        Args:
            query (str): The search query to rank documents against
            documents (List[Union[str, Dict[str, Any]]]): List of documents to rerank.
                Can be either:
                - List of strings: Each string is treated as a document
                - List of dictionaries: Each dict should have a "text" field
            **kwargs: Additional parameters:
                - top_n (int): Number of top documents to return (default: all documents)
                - return_documents (bool): Whether to return document text in results (default: True)
                - max_chunks_per_doc (int): Maximum chunks per document for processing

        Returns:
            RerankResponse: Object containing:
                - id (str): Unique identifier for the rerank request
                - results (List[RerankDocument]): List of reranked documents with:
                    - index (int): Original index of the document in input list
                    - relevance_score (float): Relevance score (higher = more relevant)
                    - document (Union[str, Dict]): Document content (if return_documents=True)
                - meta (Optional[Dict]): Additional metadata about the request

        Raises:
            ValueError: If required parameters are missing or if the API request fails
        """
        self._validate_required_params({
            "query": query,
            "documents": documents
        })
        self._validate_optional_params(kwargs)
        
        # Validate documents structure
        for i, doc in enumerate(documents):
            if isinstance(doc, str) and not doc.strip():
                raise ValueError(f"Document {i} must not be empty")
            elif isinstance(doc, dict):
                if "text" not in doc or not doc["text"]:
                    raise ValueError(f"Document {i} must have a valid 'text' field")
            elif not isinstance(doc, (str, dict)):
                raise ValueError(f"Document {i} must be a string or dictionary")
        
        if self.model_id is None:
            raise ValueError("Model ID must is not set for this instance")
        
        data = {
            "model": self.model_id,
            "query": query,
            "documents": documents
        }
        data.update(kwargs)
        
        response = self._send_request(
            method="POST",
            endpoint="/v1/rerank",
            json_data=data
        )
        
        return RerankResponse.from_dict(response["result"])
