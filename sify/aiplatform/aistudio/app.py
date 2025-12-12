import json
import os
import mimetypes
import requests
from typing import Any, Dict, Generator, List, Optional, Union
from sify.aiplatform.aistudio.types import ChatCompletionResponse, ChatCompletionStreamResponse, FileObject, MessageFile, AgentThought, RetrieverResource, Message, Conversation, FileUploadResponse


class AIApplication:
    def __init__(self, base_url: str, api_key: str):
        """
        Initialize the AIApplication with a base URL and api  key.

        Args:
            base_url (str): The base URL for the API (e.g., https://copilot-dev.sifymdp.digital/v1).
            api_key (str): The API key for authentication.

        Raises:
            ValueError: If base_url or api_key is empty or invalid.
        """
        if not base_url:
            raise ValueError("Base URL must be provided")
        if not api_key:
            raise ValueError("API key must be provided")

        self.base_url = base_url.rstrip('/')
        self.api_key = api_key

    def _send_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                headers=headers,
                stream=stream,
                timeout=300
            )

            if response.status_code >= 400:
                # Attempt to get error message from JSON or fallback to text
                error_msg = "Something Went Wrong"
                try:
                    err_resp = response.json()
                    if 'message' in err_resp and isinstance(err_resp['message'], str):
                        error_msg = err_resp['message']
                    else:
                        error_msg = "Output error: No valid error message provided"
                except json.JSONDecodeError:
                    error_msg = response.text if response.text else "Non-JSON Error"
                raise ValueError(error_msg)

            if stream:
                def line_generator():
                    for line in response.iter_lines(decode_unicode=True):
                        if line.startswith("data:"):
                            data_str = line[len("data:"):].strip()
                            if data_str:
                                try:
                                    yield json.loads(data_str)
                                except json.JSONDecodeError:
                                    continue
                return line_generator()

            else:
                content = response.content.decode()
                try:
                    result = json.loads(content)
                except json.JSONDecodeError:
                    if 'text/html' in response.headers.get('Content-Type', ''):
                        raise ValueError(f"HTML Response: {response.text[:100]}")
                    else:
                        raise ValueError(response.text if response.text else "Non-JSON Response")
                return {"status_code": response.status_code, "result": result}

        except requests.RequestException as e:
            error_msg = str(e).lower()
            if "timeout" in error_msg:
                error_msg = "Request timeout"
            elif "connection" in error_msg:
                error_msg = "Connection error"
            else:
                error_msg = "Something Went Wrong"
            raise ValueError(error_msg)
    def _send_file_request(
        self,
        method: str,
        endpoint: str,
        files: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
            # Note: Don't set Content-Type for multipart/form-data - requests will set it automatically
        }
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                files=files,
                data=data,
                headers=headers,
                timeout=300
            )

            if response.status_code >= 400:
                # Attempt to get error message from JSON or fallback to text
                error_msg = "Request failed"
                try:
                    err_resp = response.json()
                    if 'message' in err_resp and isinstance(err_resp['message'], str):
                        error_msg = err_resp['message']
                    else:
                        error_msg = "API error: No valid error message provided"
                except json.JSONDecodeError:
                    error_msg = response.text if response.text else "Non-JSON Error"
                raise ValueError(error_msg)

            try:
                result = response.json()
                return {"status_code": response.status_code, "result": result}
            except json.JSONDecodeError:
                if 'text/html' in response.headers.get('Content-Type', ''):
                    raise ValueError(f"HTML Response: {response.text[:100]}")
                else:
                    raise ValueError(response.text if response.text else "Non-JSON Response")

        except requests.RequestException as e:
            error_msg = str(e).lower()
            if "timeout" in error_msg:
                error_msg = "Request timeout"
            elif "connection" in error_msg:
                error_msg = "Connection error"
            else:
                error_msg = "Something Went Wrong"
            raise ValueError(error_msg)

    def _validate_required_params(self, params: Dict[str, Any]) -> None:
        for param_name, param_value in params.items():
            if not param_value:
                raise ValueError(f"{param_name} must not be empty")
        
    def chat_message(
        self,
        query: str,
        user: str,
        response_mode: str,
        inputs: Dict[str, Any] = None,
        conversation_id: Optional[str] = None,
        files: Optional[List[FileObject]] = None,
        auto_generate_name: bool = True,
        
    ) -> Union[ChatCompletionResponse, Generator[ChatCompletionStreamResponse, None, None]]:
        """
        Send a chat message to the AI application.

        Args:
            inputs (object): Additional input data as key-value pairs, corresponding to variable values defined by the App.
                             Default is an empty object {}.
            query (str): The user input/question content. Required.
            user (str): The user identifier, unique within the application, used for retrieval and statistics. Required.
            response_mode (str): Response mode, either "blocking" or "streaming". Required.
            conversation_id (str): The UUID string of the conversation to continue, based on previous chat records.
                                  To automatically generate for a new conversation, set to None.
            files (object): Array of file objects for multimodal input (e.g., images combined with text).
                            Only available when the model supports Vision capability. Defaults to None.
                            Each file object contains:
                            - type (str): File type, currently only "image" is supported.
                            - transfer_method (str): Transfer method, either "remote_url" or "local_file".
                            - url (str): Image URL, required if transfer_method is "remote_url".
                            - upload_file_id (str): Uploaded file ID, required if transfer_method is "local_file",
                                                    obtained via the /files/upload Output .
            auto_generate_name (bool): Whether to auto-generate the conversation title. Defaults to True.
                                       If False, the conversation rename Output  can be used to generate a title asynchronously.

        Returns:
              - If response_mode="blocking":
                - ChatCompletionResponse: An object containing:
                - id (Optional[str]): Unique identifier for the response (optional).
                - event (str): Event type, typically "message".
                - message_id (str): Unique message ID (UUID).
                - conversation_id (str): Conversation ID (UUID).
                - mode (str): Application mode, fixed as "chat".
                - answer (str): Complete response content from the AI.
                - metadata (ChatMetaData): Metadata object containing:
                    - usage (ChatMetaUsage): Usage details including:
                    - prompt_tokens (int): Number of tokens in the prompt.
                    - prompt_unit_price (float): Price per prompt token.
                    - prompt_price (float): Total prompt cost.
                    - prompt_price_unit (str): Unit for prompt price.
                    - completion_tokens (int): Number of tokens in the completion.
                    - completion_unit_price (float): Price per completion token.
                    - completion_price (float): Total completion cost.
                    - completion_price_unit (str): Unit for completion price.
                    - total_tokens (int): Total tokens used.
                    - total_price (float): Total cost.
                    - currency (str): Currency of the cost, set to "INR".
                    - latency (float): Response latency in seconds.
                    - retriever_resources (List[RetrieverResource]): List of cited resources, each with:
                    - position (int): Position in the response.
                    - dataset_id (str): Dataset ID (UUID).
                    - dataset_name (str): Dataset name.
                    - document_id (str): Document ID (UUID).
                    - document_name (str): Document name.
                    - segment_id (str): Segment ID (UUID).
                    - score (float): Relevance score.
                    - content (str): Content of the retrieved resource.
                - created_at (int): Message creation timestamp (Unix epoch).
                - task_id (Optional[str]): Task ID for tracking (optional).
            - If response_mode="streaming":
                - Iterator of ChatCompletionStreamResponse: An iterator yielding ChatCompletionStreamResponse objects, each containing:
                - event (str): Event type (e.g., "message", "chunk", or "done").
                - task_id (Optional[str]): Task ID for tracking (optional).
                - message_id (Optional[str]): Unique message ID (UUID).
                - conversation_id (Optional[str]): Conversation ID (UUID).
                - answer (Optional[str]): Partial or complete response content from the AI.
                - created_at (Optional[int]): Message creation timestamp (Unix epoch).
                - metadata (Optional[Dict[str, Any]]): Metadata for the response (optional).
                - id (Optional[str]): Unique identifier for the response (optional).

        Raises:
            ValueError: If query or user is empty, conversation_id is not a valid UUID, or Output  request fails.
        """
        if response_mode not in ["blocking", "streaming"]:
            raise ValueError("response_mode must be 'blocking' or 'streaming'")

        self._validate_required_params({
            "query": query,
            "user": user,
            "response_mode": response_mode
        })

        data = {
            "inputs": inputs or {},
            "query": query,
            "user": user,
            "response_mode": response_mode,
            "auto_generate_name": auto_generate_name
        }

        if conversation_id:
            data["conversation_id"] = conversation_id

        if files:
            data["files"] = [file.to_dict() for file in files]
        
        def stream_mode():
            response_generator = self._send_request(
                method="POST",
                endpoint="/chat-messages",
                json_data=data,
                stream=True
            )
            for line in response_generator:
                yield ChatCompletionStreamResponse.from_dict(line)

        def blocking_mode():
            response = self._send_request(
                method="POST",
                endpoint="/chat-messages",
                json_data=data,
                stream=False
            )
            return ChatCompletionResponse.from_dict(response["result"])


        if response_mode == "streaming":
            return stream_mode()
        else:
            return blocking_mode()
        
    def file_upload(self, file_path: str, user: str) -> FileUploadResponse:
        """
        Upload a file (currently only images are supported) for use when sending messages, 
        enabling multimodal understanding of images and text. Supports png, jpg, jpeg, webp, gif formats.

        Args:
            file_path (str): The path to the file to be uploaded. Required.
            user (str): User identifier, defined by the developer's rules, must be unique within the application. Required.

        Returns:
            FileUploadResponse: Upload response containing:
                - id (str): File ID (UUID).
                - name (str): File name.
                - size (int): File size in bytes.
                - extension (str): File extension.
                - mime_type (str): File mime-type.
                - created_by (str): End-user ID (UUID).
                - created_at (int): Creation timestamp.

        Raises:
            ValueError: If file_path or user is empty, file doesn't exist, or upload request fails.
            FileNotFoundError: If the specified file path doesn't exist.
        """
        
        self._validate_required_params({
            "file_path": file_path,
            "user": user
        })
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get file information
        file_name = os.path.basename(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # Validate file type (only images supported)
        supported_types = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'image/gif']
        if mime_type not in supported_types:
            raise ValueError(f"Unsupported file type: {mime_type}. Supported types: {', '.join(supported_types)}")
        
        # Prepare file and data for upload
        with open(file_path, 'rb') as file:
            files = {
                'file': (file_name, file, mime_type)
            }
            data = {
                'user': user
            }
            
            # Use the centralized file request method
            response = self._send_file_request(
                method="POST",
                endpoint="/files/upload",
                files=files,
                data=data
            )
            
            return FileUploadResponse.from_dict(response["result"])

    def get_conversation_messages(self, user: str, conversation_id: str, 
                                 first_id: Optional[str] = None, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Get messages from a specific conversation in a scrolling load format, returning the latest {limit} messages in reverse order.

        Args:
            user (str): The user identifier, unique within the application, used for retrieval and statistics. Required.
            conversation_id (str): The UUID string of the conversation to retrieve messages from. Defaults to None.
            first_id (str): The UUID string of the first message on the current page. Defaults to None.
            limit (int): Maximum number of messages to retrieve, defaults to 20.

        Returns:
            object: Output response containing:
                    - limit (int): Number of messages returned, defaults to 20 or system limit if exceeded.
                    - has_more (bool): Whether there are more messages to retrieve.
                    - data (array[object]): List of message objects, each containing:
                        - id (str): Message ID (UUID).
                        - conversation_id (str): Conversation ID (UUID).
                        - inputs (object): User input parameters as key-value pairs.
                        - query (str): User input/question content.
                        - answer (str): Response message content.
                        - message_files (array[object]): List of message files, each with:
                            - id (str): File ID (UUID).
                            - type (str): File type, currently only "image".
                            - url (str): Preview image URL.
                            - belongs_to (str): "user" or "assistant".
                        - feedback (object): Feedback information with rating ("like", "dislike", "null").
                        - retriever_resources (array[object]): Citation and attribution list, each with:
                            - position (int): Position in the response.
                            - dataset_id (str): Dataset ID (UUID).
                            - dataset_name (str): Dataset name.
                            - document_id (str): Document ID (UUID).
                            - document_name (str): Document name.
                            - segment_id (str): Segment ID (UUID).
                            - score (float): Relevance score.
                            - content (str): Content of the retrieved resource.
                        - agent_thoughts (array[object]): Agent thoughts (empty for Basic Assistant), each with:
                            - id (str): Agent thought ID (UUID).
                            - message_id (str): Message ID (UUID).
                            - position (int): Position of the thought.
                            - thought (str): LLM's thought content.
                            - tool (str): List of tools called, separated by ";".
                            - tool_input (str): Tool input in JSON format (e.g., {"dalle3": {"prompt": "a cute cat"}}).
                            - observation (str): Response from tool calls.
                            - created_at (int): Creation timestamp.
                            - message_files (array[str]): List of file IDs (UUIDs).
                        - created_at (int): Creation timestamp (e.g., 1705395332).

        Raises:
            ValueError: If user is empty, conversation_id or first_id is not a valid UUID, or Output  request fails.
"""
        self._validate_required_params({
            "user": user,
            "conversation_id": conversation_id
        })        
        params = {
            "user": user,
            "conversation_id": conversation_id
        }
        if first_id is not None:
            params["first_id"] = first_id
        if limit is not None:
            params["limit"] = limit

        response = self._send_request(method="GET", endpoint="/messages", params=params)
        result = response["result"]
        messages = [
            Message(
                id=msg["id"],
                conversation_id=msg["conversation_id"],
                inputs=msg["inputs"],
                query=msg["query"],
                answer=msg["answer"],
                message_files=[MessageFile(**mf) for mf in msg["message_files"]],
                feedback=msg["feedback"],
                retriever_resources=[RetrieverResource(**rr) for rr in msg["retriever_resources"]],
                agent_thoughts=[AgentThought(**at) for at in msg["agent_thoughts"]],
                created_at=msg["created_at"]
            ) for msg in result["data"]
        ]
        return {
            "limit": result["limit"],
            "has_more": result["has_more"],
            "data": messages
        }

    def get_conversations(self, user: str, last_id: Optional[str] = None, 
                          limit: Optional[int] = None, pinned: Optional[bool] = None) -> Dict[str, Any]:
        """
        Retrieve the conversation list for the current user.

        Args:
            user (str): The user identifier, unique within the application. Required.
            last_id (Optional[str]): The UUID string of the last conversation on the current page. Defaults to None.
            limit (Optional[int]): Maximum number of conversations to return, defaults to 20.
            pinned (Optional[bool]): Return only pinned conversations (True) or non-pinned (False). Defaults to None.

        Returns:
             object: Output response containing:
                    - limit (int): Number of conversations returned, defaults to 20 or system limit if exceeded.
                    - has_more (bool): Whether there are more conversations to retrieve.
                    - data (array[object]): List of conversation objects, each containing:
                    - id (str): Conversation ID (UUID).
                    - name (str): Conversation name, defaults to a snippet of the first question.
                    - inputs (object): User input parameters as key-value pairs.
                    - introduction (str): Conversation introduction.
                    - created_at (int): Creation timestamp (e.g., 1705395332).
                    - status (str): Conversation status, typically "normal".

        Raises:
            ValueError: If user is empty, or Output  request fails.
        """
        self._validate_required_params({
            "user": user
        })

        params = {"user": user}
        if last_id:
            params["last_id"] = last_id
        if limit is None:
            limit = 20
        params["limit"] = limit
        if pinned is not None:
            params["pinned"] = pinned
        response = self._send_request(method="GET", endpoint="/conversations", params=params)
        result = response["result"]
        conversations = [
            Conversation(**conv) for conv in result["data"]
        ]
        return {
            "limit": result["limit"],
            "has_more": result["has_more"],
            "data": conversations
        }

    def send_message_feedback(self, message_id: str, user: str, rating: str) -> Dict[str, str]:
        """
        Send feedback for a specific message to optimize application outputs.

        Args:
            message_id (str): The UUID string of the message to send feedback for. Required.
            user (str): The user identifier, unique within the application. Required.
            rating (str): The feedback rating, one of "like", "dislike", or "null".

        Returns:
            object: Output response containing:
                    - result (str): "success".

        Raises:
            ValueError: If message_id, user, or rating is empty, or Output  request fails.
        """
        self._validate_required_params({
            "message_id": message_id,
            "user": user,
            "rating": rating
        })

        data = {
            "rating": rating,
            "user": user
        }
        response = self._send_request(
            method="POST",
            endpoint=f"/messages/{message_id}/feedbacks",
            json_data=data
        )
        return response["result"]

    def rename_conversation(self, conversation_id: str, user: str, name: Optional[str] = None, 
                           auto_generate: bool = False) -> Conversation:
        """
        Rename a conversation.

        Args:
            conversation_id (str): The UUID string of the conversation to rename. Required.
            user (str): The user identifier, unique within the application. Required.
            name (str): The new name for the conversation. Defaults to None if auto_generate is True.
            auto_generate (bool): Whether to auto-generate the conversation title. Defaults to False.

        Returns:
            object: Output response containing:
                    - id (str): Conversation ID (UUID).
                    - name (str): Conversation name.
                    - inputs (object): User input parameters as key-value pairs.
                    - introduction (str): Conversation introduction.
                    - created_at (int): Creation timestamp (e.g., 1705395332).

        Raises:
            ValueError: If conversation_id or user is empty, name is empty when auto_generate is False.
        """

        self._validate_required_params({
            "conversation_id": conversation_id,
            "user": user
        })
        if not auto_generate and not name:
            raise ValueError("Name must not be empty when auto_generate is False")

        data = {
            "user": user,
            "auto_generate": auto_generate
        }
        if name:
            data["name"] = name

        response = self._send_request(
            method="POST",
            endpoint=f"/conversations/{conversation_id}/name",
            json_data=data
        )
        return Conversation(**response["result"])

    def stop_generate_message(self, task_id: str, user: str) -> Dict[str, str]:
        """
        Stop generating a message. Only supported in streaming mode.

        Args:
            task_id (str): Task ID obtained from the streaming chunk return.
            user (str): User identifier, must be consistent with the user passed in the send message interface.

        Returns:
            dict: Output response containing result.
                result (str): "success".

        Raises:
            ValueError: If task_id or user is empty, or request fails.
        """
        self._validate_required_params({
            "task_id": task_id,
            "user": user
        })

        data = {"user": user}

        response = self._send_request(
            method="POST",
            endpoint=f"/chat-messages/{task_id}/stop",
            json_data=data
        )
        
        return response["result"]
