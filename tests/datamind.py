import json
from sify.aiplatform.aistudio.datamind import DataMind

class DataMindApp(DataMind):
    def __init__(self, base_url=None, api_key=None):
        base_url = "https://copilot-dev.sifymdp.digital/v1"
        api_key = "dataset-xY8xMDZ0vsgIGGthRIEX478r"
        super().__init__(base_url, api_key)

def test_create_knowledge():
    """
    Test the create_knowledge method.
    """
    try:
        app = DataMindApp()
        response = app.create_knowledge(name="TestDataset")
        print("Create Knowledge Response:")
        print(json.dumps(response, indent=2))
        return response.get("id")  # Extract dataset_id from response
    except Exception as e:
        print(f"Error in create_knowledge test: {str(e)}")
        return None

def test_list_knowledge():
    """
    Test the list_knowledge method.
    """
    try:
        app = DataMindApp()
        response = app.list_knowledge(page=1, limit=20)
        print("List Knowledge Response:")
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error in list_knowledge test: {str(e)}")

def test_create_document_from_text(dataset_id: str):
    """
    Test the create_document_from_text method.
    """
    try:
        app = DataMindApp()
        response = app.create_document_from_text(
            dataset_id=dataset_id,
            name="TestDocument",
            text="This is a sample document for testing.",
            indexing_technique="high_quality",
            process_rule={"mode": "automatic"}
        )
        print("Create Document from Text Response:")
        print(json.dumps(response, indent=2))
        return response.get("document", {}).get("id"), response.get("batch")  # Extract document_id and batch
    except Exception as e:
        print(f"Error in create_document_from_text test: {str(e)}")
        return None, None

def test_create_document_from_file(dataset_id: str):
    """
    Test the create_document_from_file method.
    """
    try:
        app = DataMindApp()
        response = app.create_document_from_file(
            dataset_id=dataset_id,
            file_path="sample.txt",
            name="TestFileDocument",
            indexing_technique="high_quality"
        )
        print("Create Document from File Response:")
        print(json.dumps(response, indent=2))
        return response.get("document", {}).get("id"), response.get("batch")  # Extract document_id and batch
    except Exception as e:
        print(f"Error in create_document_from_file test: {str(e)}")
        return None, None

def test_update_document_text(dataset_id: str, document_id: str):
    """
    Test the update_document_text method.
    """
    try:
        app = DataMindApp()
        response = app.update_document_text(
            dataset_id=dataset_id,
            document_id=document_id,
            name="UpdatedTestDocument",
            text="This is updated text for the document."
        )
        print("Update Document Text Response:")
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error in update_document_text test: {str(e)}")

def test_update_document_file(dataset_id: str, document_id: str):
    """
    Test the update_document_file method.
    """
    try:
        app = DataMindApp()
        response = app.update_document_file(
            dataset_id=dataset_id,
            document_id=document_id,
            name="UpdatedTestFileDocument",
            file_path="sample.txt"
        )
        print("Update Document File Response:")
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error in update_document_file test: {str(e)}")

def test_get_embedding_status(dataset_id: str, batch: str):
    """
    Test the get_embedding_status method.
    """
    try:
        app = DataMindApp()
        response = app.get_embedding_status(
            dataset_id=dataset_id,
            batch=batch
        )
        print("Get Embedding Status Response:")
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error in get_embedding_status test: {str(e)}")

def test_list_documents(dataset_id: str):
    """
    Test the list_documents method.
    """
    try:
        app = DataMindApp()
        response = app.list_documents(dataset_id=dataset_id)
        print("List Documents Response:")
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error in list_documents test: {str(e)}")

def test_delete_document(dataset_id: str, document_id: str):
    """
    Test the delete_document method.
    """
    try:
        app = DataMindApp()
        response = app.delete_document(
            dataset_id=dataset_id,
            document_id=document_id
        )
        print("Delete Document Response:")
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error in delete_document test: {str(e)}")

def test_delete_knowledge(dataset_id: str):
    """
    Test the delete_knowledge method.
    """
    try:
        app = DataMindApp()
        response = app.delete_knowledge(dataset_id=dataset_id)
        print("Delete Knowledge Response:")
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error in delete_knowledge test: {str(e)}")

if __name__ == "__main__":
    # Placeholder IDs from previous chat_message response
    fallback_dataset_id = "101b4c97-fc2e-463c-90b1-5261a4cdcafb"
    fallback_document_id = "8dd1ad74-0b5f-4175-b735-7d98bbbb4e00"
    fallback_batch_id = "ed599c7f-2766-4294-9d1d-e5235a61270a"

    print("Testing create_knowledge")
    print("-" * 40)
    dataset_id = test_create_knowledge()
    test_dataset_id = dataset_id or fallback_dataset_id

    print("\nTesting list_knowledge")
    print("-" * 40)
    test_list_knowledge()

    print("\nTesting create_document_from_text")
    print("-" * 40)
    document_id, batch_id = test_create_document_from_text(test_dataset_id)
    test_document_id = document_id or fallback_document_id
    test_batch_id = batch_id or fallback_batch_id

    print("\nTesting create_document_from_file")
    print("-" * 40)
    file_document_id, file_batch_id = test_create_document_from_file(test_dataset_id)
    test_file_document_id = file_document_id or fallback_document_id
    test_file_batch_id = file_batch_id or fallback_batch_id

    print("\nTesting update_document_text")
    print("-" * 40)
    test_update_document_text(test_dataset_id, test_document_id)

    print("\nTesting update_document_file")
    print("-" * 40)
    test_update_document_file(test_dataset_id, test_file_document_id)

    print("\nTesting get_embedding_status")
    print("-" * 40)
    test_get_embedding_status(test_dataset_id, test_batch_id)

    print("\nTesting list_documents")
    print("-" * 40)
    test_list_documents(test_dataset_id)

    print("\nTesting delete_document")
    print("-" * 40)
    test_delete_document(test_dataset_id, test_document_id)

    print("\nTesting delete_knowledge")
    print("-" * 40)
    test_delete_knowledge(test_dataset_id)