import requests
import json
from typing import Dict, Any, Optional
from sify.aiplatform.aistudio.types import ProcessRule, DocumentResponse, Document, SegmentationRule, PreProcessingRule, Dataset, BatchStatus, ListDocumentsResponse, DatasetResponse, ListKnowledgeResponse, BatchStatusResponse

class DataMind:
    def __init__(self, base_url: str, api_key: str):
        """
        Initialize the DataMind client with the base URL and API key.

        Args:
            base_url (str): The base URL of the DataMind API (e.g., https://copilot-dev.sifymdp.digital/v1).
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

    def _send_request(self, method: str, endpoint: str, json_data: Dict[str, Any] = None, 
                     params: Dict[str, Any] = None, files: Dict[str, Any] = None) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json" if not files else None
        }

        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                headers=headers,
                files=files,
                timeout=300
            )
            if response.status_code >= 400:
                error_msg = f"{response.status_code} {response.reason}"
                try:
                    error_response = response.json()
                    if 'message' in error_response and isinstance(error_response['message'], str):
                        error_msg = error_response['message']
                except json.JSONDecodeError:
                    if response.status_code == 404:
                        error_msg = response.reason
                    elif 'text/html' in response.headers.get('Content-Type', ''):
                        error_msg = f"HTML Error: {response.text[:100]}"
                    else:
                        error_msg = response.text if response.text else "Non-JSON Error"
                raise ValueError(error_msg)

            try:
                result = response.json()
            except json.JSONDecodeError:
                if 'text/html' in response.headers.get('Content-Type', ''):
                    result = f"HTML Response: {response.text[:100]}"
                else:
                    result = response.text if response.text else "Non-JSON Response"
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
        
    def _validate_required_params(self, params: Dict[str, Any]) -> None:
        for param_name, param_value in params.items():
            if not param_value:
                raise ValueError(f"{param_name} must not be empty")

    def create_document_from_text(self, dataset_id: str, name: str, text: str, 
                                 indexing_technique: str = "high_quality", process_rule: Optional[ProcessRule] = None) -> DocumentResponse:
        """
        Create a document in a dataset from text content.

        Args:
            dataset_id (str): The UUID string of the dataset to create the document in. Required.
            name (str): The name of the document. Required.
            text (str): The text content of the document. Required.
            indexing_technique (str): The indexing technique to use. Defaults to "high_quality".
            process_rule (Optional[ProcessRule]): process_rule (Optional[ProcessRule]): Custom processing rules with mode (str)(Cleaning, segmentation mode, automatic / custom) and rules (Dict[str, Any]) (pre_processing_rules, segmentation). Defaults to None.
        Returns:
             object: Output response containing:
                    - document (object): Document details with:
                        - id (str): Document ID (UUID).
                        - position (int): Document position (e.g., 1).
                        - data_source_type (str): Source type, e.g., "upload_file".
                        - data_source_info (object): Source information, e.g., {"upload_file_id": ""}.
                        - dataset_process_rule_id (str): Process rule ID (UUID).
                        - name (str): Document name (e.g., "text.txt").
                        - created_from (str): Creation source, e.g., "api".
                        - created_by (str): Creator ID (UUID).
                        - created_at (int): Creation timestamp (e.g., 1695690280).
                        - tokens (int): Token count.
                        - indexing_status (str): Status, e.g., "waiting".
                        - error (null or str): Error message if any.
                        - enabled (bool): Whether the document is enabled.
                        - disabled_at (null or int): Timestamp when disabled.
                        - disabled_by (null or str): User who disabled the document.
                        - archived (bool): Whether the document is archived.
                        - display_status (str): Display status, e.g., "queuing".
                        - word_count (int): Word count.
                        - hit_count (int): Hit count.
                        - doc_form (str): Document format, e.g., "text_model".
                    - batch (str): Batch ID for the document creation.

        Raises:
            ValueError: If dataset_id, name, or text is empty, or Output request fails.
        """
        self._validate_required_params({
            "dataset_id": dataset_id,
            "name": name,
            "text": text
        })

        if process_rule is None:
            process_rule = ProcessRule(mode="automatic")

        data = {
            "name": name,
            "text": text,
            "indexing_technique": indexing_technique,
            "process_rule": process_rule.to_dict()
        }
        
        response = self._send_request(
            method="POST", 
            endpoint=f"/datasets/{dataset_id}/document/create_by_text", 
            json_data=data
        )
        return DocumentResponse(
            document=Document(**response["result"]["document"]),
            batch=response["result"]["batch"]
        )

    def create_document_from_file(self, dataset_id: str, file_path: str,
                                 indexing_technique: str = "high_quality", process_rule: Optional[ProcessRule] = None) -> DocumentResponse:
        """
        Create a document in a dataset from a file.

        Args:
            dataset_id (str): The UUID string of the dataset to create the document in. Required.
            file_path (str): The path to the file to be uploaded. Required.
            indexing_technique (str): The indexing technique to use. Defaults to "high_quality".
            process_rule (Optional[ProcessRule]): Custom processing rules with mode (str)(Cleaning, segmentation mode, automatic / custom) and rules (Dict[str, Any]) (pre_processing_rules, segmentation). Defaults to None.

        Returns:
            object: Output response containing:
                    - document (object): Document details with:
                        - id (str): Document ID (UUID).
                        - position (int): Document position (e.g., 1).
                        - data_source_type (str): Source type, e.g., "upload_file".
                        - data_source_info (object): Source information, e.g., {"upload_file_id": ""}.
                        - dataset_process_rule_id (str): Process rule ID (UUID).
                        - name (str): Document name (e.g., "message.txt").
                        - created_from (str): Creation source, e.g., "api".
                        - created_by (str): Creator ID (UUID).
                        - created_at (int): Creation timestamp (e.g., 1695308667).
                        - tokens (int): Token count.
                        - indexing_status (str): Status, e.g., "waiting".
                        - error (null or str): Error message if any.
                        - enabled (bool): Whether the document is enabled.
                        - disabled_at (null or int): Timestamp when disabled.
                        - disabled_by (null or str): User who disabled the document.
                        - archived (bool): Whether the document is archived.
                        - display_status (str): Display status, e.g., "queuing".
                        - word_count (int): Word count.
                        - hit_count (int): Hit count.
                        - doc_form (str): Document format, e.g., "text_model".
                    - batch (str): Batch ID for the document creation.

        Raises:
            ValueError: If dataset_id, file_path, or name is empty, or Output request fails.
        """
        self._validate_required_params({
            "dataset_id": dataset_id,
            "file_path": file_path
        })
        if process_rule is None:
            process_rule = ProcessRule(
                mode="custom",
                rules={
                    "pre_processing_rules": [
                        PreProcessingRule(id="remove_extra_spaces", enabled=True),
                        PreProcessingRule(id="remove_urls_emails", enabled=True)
                    ],
                    "segmentation": SegmentationRule(separator="###", max_tokens=500)
                }
            )
            
        data = {
            "indexing_technique": indexing_technique,
            "process_rule": process_rule.to_dict()
        }
        
        with open(file_path, 'rb') as file:
            files = {
                'data': (None, json.dumps(data), 'text/plain'),
                'file': file
            }
            response = self._send_request(
                method="POST",
                endpoint=f"/datasets/{dataset_id}/document/create_by_file",
                files=files
            )
        return DocumentResponse(
            document=Document(**response["result"]["document"]),
            batch=response["result"]["batch"]
        )

    def create_knowledge(self, name: str) -> DatasetResponse:
        """
        Create a new empty knowledge dataset.

        Args:
            name (str): The name of the knowledge dataset. Required.

        Returns:
            object: Output response containing:
                    - id (str): Dataset ID (UUID).
                    - name (str): Dataset name.
                    - description (null or str): Dataset description.
                    - provider (str): Provider, e.g., "vendor".
                    - permission (str): Permission level, e.g., "only_me".
                    - data_source_type (null or str): Data source type, e.g., "upload_file".
                    - indexing_technique (null or str): Indexing technique used.
                    - app_count (int): Number of associated apps.
                    - document_count (int): Number of documents.
                    - word_count (int): Total word count.
                    - created_by (str): Creator ID (UUID).
                    - created_at (int): Creation timestamp (e.g., 1695636173).
                    - updated_by (str): Updater ID (UUID).
                    - updated_at (int): Update timestamp (e.g., 1695636173).
                    - embedding_model (null or str): Embedding model used.
                    - embedding_model_provider (null or str): Embedding model provider.
                    - embedding_available (null or bool): Whether embedding is available.
        Raises:
            ValueError: If name is empty or Output request fails.
        """
        self._validate_required_params({"name": name})
        data = {"name": name}
        response = self._send_request(method="POST", endpoint="/datasets", json_data=data)
        return DatasetResponse(**response["result"])

    def list_knowledge(self, page: int = 1, limit: int = 20) -> ListKnowledgeResponse:
        """
        List all knowledge datasets.

        Args:
            page (int): The page number to retrieve. Defaults to 1.
            limit (int): The maximum number of datasets to retrieve per page, range 1-100. Defaults to 20.

        Returns:
            object: Output response containing:
                    - data (array[object]): List of datasets, each with:
                        - id (str): Dataset ID (UUID).
                        - name (str): Dataset name.
                        - description (null or str): Dataset description.
                        - permission (str): Permission level, e.g., "only_me".
                        - data_source_type (null or str): Data source type, e.g., "upload_file".
                        - indexing_technique (str): Indexing technique used.
                        - app_count (int): Number of associated apps.
                        - document_count (int): Number of documents.
                        - word_count (int): Total word count.
                        - created_by (str): Creator ID (UUID).
                        - created_at (str): Creation timestamp.
                        - updated_by (str): Updater ID (UUID).
                        - updated_at (str): Update timestamp.
                    - has_more (bool): Whether there are more datasets to retrieve.
                    - limit (int): Number of items returned (1-100).
                    - total (int): Total number of datasets.
                    - page (int): Current page number.

        Raises:
            ValueError: If page or limit is less than 1 or Output request fails.
        """
        if page < 1 or limit < 1:
            raise ValueError("Page and limit must be greater than 0")
        params = {
            "page": page,
            "limit": limit
        }
        response = self._send_request(method="GET", endpoint="/datasets", params=params)
        return ListKnowledgeResponse(
            data=[Dataset(**dataset) for dataset in response["result"]["data"]],
            has_more=response["result"]["has_more"],
            limit=response["result"]["limit"],
            total=response["result"]["total"],
            page=response["result"]["page"]
        )

    def delete_knowledge(self, dataset_id: str):
        """
        Delete a knowledge dataset.

        Args:
            dataset_id (str): The UUID string of the dataset to delete. Required.

        Returns:
            object: Output response containing:
                    - status (str): "success" for successful deletion.

        Raises:
            ValueError: If dataset_id is empty or Output request fails.
        """
        self._validate_required_params({"dataset_id": dataset_id})
        response = self._send_request(method="DELETE", endpoint=f"/datasets/{dataset_id}")
        result = response["result"]
        # Handle both string and dict responses, and 204 No Content
        if response.get("status_code") == 204 or result == "No Content":
            status = "success"   
        else:
            status = "Something Went Wrong while deleteing"
        return status

    def update_document_text(self, dataset_id: str, document_id: str, name: str, text: str) -> DocumentResponse:
        """
        Update a document in a dataset with new text content.

        Args:
            dataset_id (str): The UUID string of the dataset containing the document. Required.
            document_id (str): The UUID string of the document to update. Required.
            name (str): The new name for the document. Required.
            text (str): The new text content for the document. Required.

        Returns:
            object: Output response containing:
                    - document (object): Document details with:
                        - id (str): Document ID (UUID).
                        - position (int): Document position (e.g., 1).
                        - data_source_type (str): Source type, e.g., "upload_file".
                        - data_source_info (object): Source information, e.g., {"upload_file_id": ""}.
                        - dataset_process_rule_id (str): Process rule ID (UUID).
                        - name (str): Document name (e.g., "name.txt").
                        - created_from (str): Creation source, e.g., "api".
                        - created_by (str): Creator ID (UUID).
                        - created_at (int): Creation timestamp (e.g., 1695308667).
                        - tokens (int): Token count.
                        - indexing_status (str): Status, e.g., "waiting".
                        - error (null or str): Error message if any.
                        - enabled (bool): Whether the document is enabled.
                        - disabled_at (null or int): Timestamp when disabled.
                        - disabled_by (null or str): User who disabled the document.
                        - archived (bool): Whether the document is archived.
                        - display_status (str): Display status, e.g., "queuing".
                        - word_count (int): Word count.
                        - hit_count (int): Hit count.
                        - doc_form (str): Document format, e.g., "text_model".
                    - batch (str): Batch ID for the document update.

        Raises:
            ValueError: If dataset_id, document_id, name, or text is empty, or Output request fails.
        """
        self._validate_required_params({"dataset_id": dataset_id,
                                       "document_id": document_id, 
                                       "name": name, 
                                       "text": text})
        data = {
            "name": name,
            "text": text
        }
        response = self._send_request(
            method="POST",
            endpoint=f"/datasets/{dataset_id}/documents/{document_id}/update_by_text",
            json_data=data
        )
        return DocumentResponse(
            document=Document(**response["result"]["document"]),
            batch=response["result"]["batch"]
        )

    def update_document_file(self, dataset_id: str, document_id: str, file_path: str) -> DocumentResponse:
        """
        Update a document in a dataset with a new file.

        Args:
            dataset_id (str): The UUID string of the dataset containing the document. Required.
            document_id (str): The UUID string of the document to update. Required.
            file_path (str): The path to the new file to upload. Required.

        Returns:
            object: Output response containing:
                    - document (object): Document details with:
                        - id (str): Document ID (UUID).
                        - position (int): Document position (e.g., 1).
                        - data_source_type (str): Source type, e.g., "upload_file".
                        - data_source_info (object): Source information, e.g., {"upload_file_id": ""}.
                        - dataset_process_rule_id (str): Process rule ID (UUID).
                        - name (str): Document name (e.g., "message.txt").
                        - created_from (str): Creation source, e.g., "api".
                        - created_by (str): Creator ID (UUID).
                        - created_at (int): Creation timestamp (e.g., 1695308667).
                        - tokens (int): Token count.
                        - indexing_status (str): Status, e.g., "waiting".
                        - error (null or str): Error message if any.
                        - enabled (bool): Whether the document is enabled.
                        - disabled_at (null or int): Timestamp when disabled.
                        - disabled_by (null or str): User who disabled the document.
                        - archived (bool): Whether the document is archived.
                        - display_status (str): Display status, e.g., "queuing".
                        - word_count (int): Word count.
                        - hit_count (int): Hit count.
                        - doc_form (str): Document format, e.g., "text_model".
                    - batch (str): Batch ID for the document update.

        Raises:
            ValueError: If dataset_id, document_id, name, or file_path is empty, or Output request fails.
"""
        self._validate_required_params({
            "dataset_id": dataset_id,
            "document_id": document_id,
            "file_path": file_path
        })

        data = {
            "indexing_technique": "high_quality",
            "process_rule": ProcessRule(
                mode="custom",
                rules={
                    "pre_processing_rules": [
                        PreProcessingRule(id="remove_extra_spaces", enabled=True),
                        PreProcessingRule(id="remove_urls_emails", enabled=True)
                    ],
                    "segmentation": SegmentationRule(separator="###", max_tokens=500)
                }
            ).to_dict()
        }
        
        with open(file_path, 'rb') as file:
            files = {
                'data': (None, json.dumps(data), 'text/plain'),
                'file': file
            }
            response = self._send_request(
                method="POST",
                endpoint=f"/datasets/{dataset_id}/documents/{document_id}/update_by_file",
                files=files
            )
        return DocumentResponse(
            document=Document(**response["result"]["document"]),
            batch=response["result"]["batch"]
        )

    def delete_document(self, dataset_id: str, document_id: str) -> str:
        """
        Delete a document from a dataset.

        Args:
            dataset_id (str): The UUID string of the dataset containing the document. Required.
            document_id (str): The UUID string of the document to delete. Required.

        Returns:
            object: Output response containing:
                    - result (str): "success" for successful deletion.

        Raises:
            ValueError: If dataset_id or document_id is empty.
        """
        self._validate_required_params({
            "dataset_id": dataset_id,
            "document_id": document_id
        })

        response = self._send_request(
            method="DELETE",
            endpoint=f"/datasets/{dataset_id}/documents/{document_id}"
        )
        response = response["result"]["result"]

        return response


    def get_embedding_status(self, dataset_id: str, batch: str) -> BatchStatusResponse:
        """
        Get the indexing status of a batch of documents in a dataset.

        Args:
                dataset_id (str): The UUID string of the dataset containing the documents. Required.
                batch (str): The batch ID of the uploaded documents. Required.

        Returns:
            object: Output response containing:
                    - data (array[object]): List of batch status objects, each with:
                        - id (str): Batch ID (UUID).
                        - indexing_status (str): Status, e.g., "indexing".
                        - processing_started_at (float): Timestamp when processing started.
                        - parsing_completed_at (float): Timestamp when parsing completed.
                        - cleaning_completed_at (float): Timestamp when cleaning completed.
                        - splitting_completed_at (float): Timestamp when splitting completed.
                        - completed_at (null or float): Timestamp when indexing completed.
                        - paused_at (null or float): Timestamp when indexing paused.
                        - error (null or str): Error message if any.
                        - stopped_at (null or float): Timestamp when indexing stopped.
                        - completed_segments (int): Number of completed segments.
                        - total_segments (int): Total number of segments.

        Raises:
            ValueError: If dataset_id or batch is empty, or Output request fails.
        """
        self._validate_required_params({
            "dataset_id": dataset_id,
            "batch": batch
        })

        response = self._send_request(
            method="GET",
            endpoint=f"/datasets/{dataset_id}/documents/{batch}/indexing-status"
        )
        return BatchStatusResponse(
            data=[BatchStatus(**status) for status in response["result"]["data"]]
        )

    def list_documents(self, dataset_id: str) -> ListDocumentsResponse:
        """
        List all documents in a dataset.

        Args:
            dataset_id (str): The UUID string of the dataset to list documents from. Required.

        Returns:
            object: Output response containing:
                    - data (array[object]): List of documents, each with:
                        - id (str): Document ID (UUID).
                        - position (int): Document position.
                        - data_source_type (str): Source type, e.g., "upload_file".
                        - data_source_info (object): Source information, e.g., {"upload_file_id": ""}.
                        - dataset_process_rule_id (str): Process rule ID (UUID).
                        - name (str): Document name.
                        - created_from (str): Creation source, e.g., "api".
                        - created_by (str): Creator ID (UUID).
                        - created_at (int): Creation timestamp.
                        - tokens (int): Token count.
                        - indexing_status (str): Status, e.g., "waiting".
                        - error (null or str): Error message if any.
                        - enabled (bool): Whether the document is enabled.
                        - disabled_at (null or int): Timestamp when disabled.
                        - disabled_by (null or str): User who disabled the document.
                        - archived (bool): Whether the document is archived.
                        - display_status (str): Display status, e.g., "queuing".
                        - word_count (int): Word count.
                        - hit_count (int): Hit count.
                        - doc_form (str): Document format, e.g., "text_model".
                    - has_more (bool): Whether there are more documents to retrieve.
                    - limit (int): Number of items returned (1-100).
                    - total (int): Total number of documents.
                    - page (int): Current page number.

        Raises:
            ValueError: If dataset_id is empty, or Output request fails.
        """
        self._validate_required_params({"dataset_id": dataset_id})
        response = self._send_request(
            method="GET",
            endpoint=f"/datasets/{dataset_id}/documents"
        )
        result = response["result"]
        required_fields = ["data", "has_more", "limit", "total", "page"]
        for field in required_fields:
            if field not in result:
                raise ValueError(f"Missing required field '{field}' in API response: {result}")
        return ListDocumentsResponse(
            data=[Document(**doc) for doc in result["data"]],
            has_more=result["has_more"],
            limit=result["limit"],
            total=result["total"],
            page=result["page"]
        )
