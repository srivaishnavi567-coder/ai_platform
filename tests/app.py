from sify.aiplatform.aistudio.app import AIApplication
import json

class App(AIApplication):
    def __init__(self, base_url=None, api_key=None):
        base_url = "https://copilot-dev.sifymdp.digital/v1"
        api_key = "app-OgGTCRXJTcPyZJdzJKEbBpW8"
        super().__init__(base_url, api_key)

def test_chat_message_blocking():
    """
    Test the chat_message method in blocking mode.
    """
    try:
        app = App()
        response = app.chat_message(
            inputs={},
            query="What are the specs of the iPhone 13 Pro Max?",
            user="abc-123",
            response_mode="blocking",
            conversation_id="",
            files=[{
                "type": "image",
                "transfer_method": "remote_url",
                "url": "https://chatbot.ai/logo/logo-site.png"
            }]
        )
        print("Blocking Mode Response:")
        print(json.dumps(response, indent=2))
        message_id = response.get("message_id")
        conversation_id = response.get("conversation_id")
        if message_id:
            print(f"Message ID: {message_id}")
        if conversation_id:
            print(f"Conversation ID: {conversation_id}")
        return message_id, conversation_id
    except Exception as e:
        print(f"Error in blocking mode test: {str(e)}")
        return None, None

def test_chat_message_streaming():
    """
    Test the chat_message method in streaming mode.
    """
    try:
        app = App()
        response = app.chat_message(
            inputs={},
            query="What are the specs of the iPhone 13 Pro Max?",
            user="abc-123",
            response_mode="streaming",
            conversation_id="",
            files=[{
                "type": "image",
                "transfer_method": "remote_url",
                "url": "https://chatbot.ai/logo/logo-site.png"
            }]
        )
        print("Streaming Mode Response:")
        full_answer = ""
        metadata = None
        conversation_id = None
        message_id = None
        if isinstance(response["answer"], list):
            for chunk in response["answer"]:
                if chunk.get("event") == "message":
                    answer_part = chunk.get("answer", "")
                    full_answer += answer_part
                    print(f"Answer chunk: {answer_part}")
                    if not conversation_id:
                        conversation_id = chunk.get("conversation_id")
                    if not message_id:
                        message_id = chunk.get("message_id")
                elif chunk.get("event") == "message_end":
                    metadata = chunk.get("metadata", {})
                    print("Metadata:")
                    print(json.dumps(metadata, indent=2))
                elif "error" in chunk:
                    print(f"Error in chunk: {chunk['error']}")
            print("\nFull Answer:")
            print(full_answer)
            if message_id:
                print(f"Message ID: {message_id}")
            if conversation_id:
                print(f"Conversation ID: {conversation_id}")
            return message_id, conversation_id
        else:
            print("Unexpected response format:")
            print(json.dumps(response, indent=2))
            return None, None
    except Exception as e:
        print(f"Error in streaming mode test: {str(e)}")
        return None, None

def test_get_conversation_messages(conversation_id: str):
    """
    Test the get_conversation_messages method.
    """
    try:
        app = App()
        response = app.get_conversation_messages(
            user="abc-123",
            conversation_id=conversation_id,
            limit=10
        )
        print("Get Conversation Messages Response:")
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error in get_conversation_messages test: {str(e)}")

def test_get_conversations():
    """
    Test the get_conversations method.
    """
    try:
        app = App()
        response = app.get_conversations(
            user="abc-123",
            limit=20
        )
        print("Get Conversations Response:")
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error in get_conversations test: {str(e)}")

def test_get_suggested_messages(message_id: str):
    """
    Test the get_suggested_messages method.
    """
    try:
        app = App()
        response = app.get_suggested_messages(
            message_id=message_id,
            user="abc-123"
        )
        print("Get Suggested Messages Response:")
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error in get_suggested_messages test: {str(e)}")

def test_send_message_feedback(message_id: str):
    """
    Test the send_message_feedback method.
    """
    try:
        app = App()
        response = app.send_message_feedback(
            message_id=message_id,
            user="abc-123",
            rating="like"
        )
        print("Send Message Feedback Response:")
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error in send_message_feedback test: {str(e)}")

def test_stop_chat_message(task_id: str):
    """
    Test the stop_chat_message method.
    """
    try:
        app = App()
        response = app.stop_chat_message(
            task_id=task_id,
            user="abc-123"
        )
        print("Stop Chat Message Response:")
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error in stop_chat_message test: {str(e)}")

def test_delete_conversation(conversation_id: str):
    """
    Test the delete_conversation method.
    """
    try:
        app = App()
        response = app.delete_conversation(
            conversation_id=conversation_id,
            user="abc-123"
        )
        print("Delete Conversation Response:")
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error in delete_conversation test: {str(e)}")

def test_rename_conversation(conversation_id: str):
    """
    Test the rename_conversation method.
    """
    try:
        app = App()
        response = app.rename_conversation(
            conversation_id=conversation_id,
            user="abc-123",
            name="Test Conversation"
        )
        print("Rename Conversation Response:")
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error in rename_conversation test: {str(e)}")

if __name__ == "__main__":
    print("Testing chat_message in Blocking Mode")
    print("-" * 40)
    message_id, conversation_id = test_chat_message_blocking()

    print("\nTesting chat_message in Streaming Mode")
    print("-" * 40)
    # Use IDs from streaming response if available, else blocking, else provided values
    test_message_id = message_id or "21602b41-7773-486e-8ec3-9e7ac0fe94df"
    test_conversation_id = conversation_id or "bd2f390f-4857-4448-b532-28efd3a3c6ab"
    test_task_id = "21602b41-7773-486e-8ec3-9e7ac0fe94df"  # Using message_id as placeholder; replace with actual task_id

    print("\nTesting get_conversation_messages")
    print("-" * 40)
    test_get_conversation_messages(test_conversation_id)

    print("\nTesting get_conversations")
    print("-" * 40)
    test_get_conversations()

    print("\nTesting get_suggested_messages")
    print("-" * 40)
    test_get_suggested_messages(test_message_id)

    print("\nTesting send_message_feedback")
    print("-" * 40)
    test_send_message_feedback(test_message_id)

    print("\nTesting stop_chat_message")
    print("-" * 40)
    test_stop_chat_message(test_task_id)

    print("\nTesting rename_conversation")
    print("-" * 40)
    test_rename_conversation(test_conversation_id)

    print("\nTesting delete_conversation")
    print("-" * 40)
    test_delete_conversation(test_conversation_id)