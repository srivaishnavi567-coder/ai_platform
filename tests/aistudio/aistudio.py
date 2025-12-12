# import json
# import requests
# from sify.aiplatform.aistudio.app import AIApplication
# from sify.aiplatform.aistudio.types import ChatCompletionResponse, Conversation, Message, FileObject
# import threading
# import time

# app = AIApplication(base_url="https://copilot-dev.sifymdp.digital/v1", api_key="app-OgGTCRXJTcPyZJdzJKEbBpW8")

# # # Upload a file and get a structured response
# # upload_response = app.file_upload(
# #     file_path="note.png",
# #     user="abc-123"
# # )

# # # Now you can access properties directly with proper type hints
# # print(f"File ID: {upload_response.id}")
# # print(f"File name: {upload_response.name}")

# class AIApplicationApp(AIApplication):
#     def __init__(self, base_url=None, api_key=None):
#         base_url = "https://copilot-dev.sifymdp.digital/v1"
#         # api_key = "app-OgGTCRXJTcPyZJdzJKEbBpW8"
#         api_key = "app-FHBylBZuiIBO3AeGQNlsiW7p"
#         super().__init__(base_url, api_key)

#     def get_agent_stream(self):
#         try:
#             app = AIApplicationApp()
#             response = app.chat_message(
#                 inputs={},
#                 query="i want to deploy graphmate from appfoundry",
#                 user="test_user_thinesh",
#                 response_mode="streaming",
#                 files=[]
#             )
#             for chunk in response:
#                 if not chunk:
#                     continue
#                 # Print only the answer part of each chunk
#                 if getattr(chunk, "answer", None):
#                     print(chunk.answer, end="")
#                 # Optionally, print agent thoughts if present in metadata
#                 # if getattr(chunk, "metadata", None) and chunk.metadata:
#                 #     agent_thoughts = chunk.metadata.get("agent_thoughts")
#                 #     if agent_thoughts:
#                 #         print("Agent Thoughts:", agent_thoughts)
#         except Exception as e:
#             print(f"Error in get_agent_stream: {e}")

# if __name__ == "__main__":
#     app = AIApplicationApp()
#     app.get_agent_stream()


#     # def get_suggested_messages(self, message_id: str, user: str) -> dict:
#     #     """
#     #     Get suggested next questions for a specific message.
#     #     """
#     #     self._validate_required_params({"message_id": message_id, "user": user})
#     #     params = {"user": user}
#     #     response = self._send_request(
#     #         method="GET",
#     #         endpoint=f"/messages/{message_id}/suggested",
#     #         params=params
#     #     )
#     #     return response["result"]

#     # def delete_conversation(self, conversation_id: str, user: str) -> dict:
#     #     """
#     #     Delete a conversation.
#     #     """
#     #     self._validate_required_params({"conversation_id": conversation_id, "user": user})
#     #     data = {"user": user}
#     #     response = self._send_request(
#     #         method="DELETE",
#     #         endpoint=f"/conversations/{conversation_id}",
#     #         json_data=data
#     #     )
#     #     return response["result"]

# # def test_chat_message():
# #     """
# #     Test the chat_message method in blocking mode.
# #     """
# #     try:
# #         app = AIApplicationApp()
# #         response = app.chat_message(
# #             inputs={},
# #             query="What are the specs of the iPhone 13 Pro Max?",
# #             user="test_user_thinesh",
# #             response_mode="blocking",
# #             files=[
# #                 FileObject(
# #                     type="image",
# #                     transfer_method="remote_url",
# #                     url="https://www.google.com/imgres?q=200%20rs%20note&imgurl=https%3A%2F%2Fupload.wikimedia.org%2Fwikipedia%2Fcommons%2Ff%2Ffa%2FIndia%252C_200_INR%252C_2018%252C_obverse.jpg&imgrefurl=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FIndian_200-rupee_note&docid=toY4A3TL-AMDTM&tbnid=h57KqNwk7Vl9SM&vet=12ahUKEwjen7WPm4KPAxVMSmwGHQE1IngQM3oECBoQAA..i&w=1166&h=497&hcb=2&ved=2ahUKEwjen7WPm4KPAxVMSmwGHQE1IngQM3oECBoQAA"
# #                 )
# #             ]
# #         )
# #         print("Chat Message Response:")
# #         print(json.dumps(response.to_dict(), indent=2))
# #         print(f"   📧 Message ID: {response.to_dict()['message_id']}"
# #               f"\n   💬 Conversation ID: {response.to_dict()['conversation_id']}")
# #         return response.to_dict()['message_id'], response.to_dict()['conversation_id']
    
# #     except Exception as e:
# #         print(f"Error in chat_message test: {str(e)}")
# #         if isinstance(e, requests.HTTPError) and e.response is not None:
# #             print(f"HTTP Error Details: {e.response.text}")
# #         return None, None
    
# # def test_chat_message_streaming():
# #     """
# #     Test the chat_message method in streaming mode and demonstrate stop_generate_message.
# #     """
# #     app = AIApplicationApp()
# #     stop_info = {"task_id": None, "stopped": False}
# #     output = ""
# #     try:
# #         stream = app.chat_message(
# #             query="Tell me a long story about AI in India.",
# #             user="test_user_thinesh",
# #             response_mode="streaming"
# #         )
# #         def consume_stream():
# #             for chunk in stream:
# #                 if hasattr(chunk, 'task_id') and chunk.task_id and not stop_info["task_id"]:
# #                     stop_info["task_id"] = chunk.task_id
# #                 if chunk.answer:
# #                     nonlocal output
# #                     output += chunk.answer
# #                     print(chunk.answer, end="", flush=True)
# #                 if stop_info["stopped"]:
# #                     break
# #         t = threading.Thread(target=consume_stream)
# #         t.start()
# #         time.sleep(4)
# #         stop_result = None
# #         if stop_info["task_id"]:
# #             print("\nAttempting to stop generation...")
# #             result = app.stop_generate_message(task_id=stop_info["task_id"], user="test_user_thinesh")
# #             print(f"Stop Result: {result['result']}")
# #             stop_info["stopped"] = True
# #             stop_result = result['result']
# #         else:
# #             print("\nWarning: No task_id received from stream, stop_generate_message not called.")
# #             stop_result = "no task_id"
# #         return stop_result
# #     except Exception as e:
# #         print(f"Error in chat_message_streaming test: {str(e)}")
# #         if isinstance(e, requests.HTTPError) and e.response is not None:
# #             print(f"HTTP Error Details: {e.response.text}")
# #         return "error"

# # def test_get_conversation_messages(conversation_id: str):
# #     """
# #     Test the get_conversation_messages method.
# #     """
# #     if not conversation_id:
# #         print("Warning: No valid conversation_id provided. Skipping get_conversation_messages test.")
# #         return
# #     try:
# #         app = AIApplicationApp()
# #         response = app.get_conversation_messages(
# #             user="test_user_thinesh",
# #             conversation_id=conversation_id
# #         )
# #         response_dict = {
# #             "limit": response["limit"],
# #             "has_more": response["has_more"],
# #             "data": [msg.to_dict() for msg in response["data"]]
# #         }
# #         print("Get Conversation Messages Response:")
# #         print(json.dumps(response_dict, indent=2))
# #     except Exception as e:
# #         print(f"Error in get_conversation_messages test: {str(e)}")
# #         if isinstance(e, requests.HTTPError) and e.response is not None:
# #             print(f"HTTP Error Details: {e.response.text}")

# # def test_get_conversations():
# #     """
# #     Test the get_conversations method.
# #     """
# #     try:
# #         app = AIApplicationApp()
# #         response = app.get_conversations(user="test_user_thinesh", limit=10)
# #         response_dict = {
# #             "limit": response["limit"],
# #             "has_more": response["has_more"],
# #             "data": [conv.to_dict() for conv in response["data"]]
# #         }
# #         print("Get Conversations Response:")
# #         print(json.dumps(response_dict, indent=2))
# #     except Exception as e:
# #         print(f"Error in get_conversations test: {str(e)}")
# #         if isinstance(e, requests.HTTPError) and e.response is not None:
# #             print(f"HTTP Error Details: {e.response.text}")

# # def test_get_suggested_messages(message_id: str):
# #     """
# #     Test the get_suggested_messages method.
# #     """
# #     if not message_id:
# #         print("Warning: No valid message_id provided. Skipping get_suggested_messages test.")
# #         return
# #     try:
# #         app = AIApplicationApp()
# #         response = app.get_suggested_messages(message_id=message_id, user="test_user_thinesh")
# #         print("Get Suggested Messages Response:")
# #         print(json.dumps(response, indent=2))
# #     except Exception as e:
# #         print(f"Error in get_suggested_messages test: {str(e)}")
# #         if isinstance(e, requests.HTTPError) and e.response is not None:
# #             print(f"HTTP Error Details: {e.response.text}")

# # def test_send_message_feedback(message_id: str):
# #     """
# #     Test the send_message_feedback method.
# #     """
# #     if not message_id:
# #         print("Warning: No valid message_id provided. Skipping send_message_feedback test.")
# #         return
# #     try:
# #         app = AIApplicationApp()
# #         response = app.send_message_feedback(
# #             message_id=message_id,
# #             user="test_user_thinesh",
# #             rating="like"
# #         )
# #         print("Send Message Feedback Response:")
# #         print(json.dumps(response, indent=2))
# #     except Exception as e:
# #         print(f"Error in send_message_feedback test: {str(e)}")
# #         if isinstance(e, requests.HTTPError) and e.response is not None:
# #             print(f"HTTP Error Details: {e.response.text}")

# # def test_delete_conversation(conversation_id: str):
# #     """
# #     Test the delete_conversation method.
# #     """
# #     if not conversation_id:
# #         print("Warning: No valid conversation_id provided. Skipping delete_conversation test.")
# #         return
# #     try:
# #         app = AIApplicationApp()
# #         response = app.delete_conversation(conversation_id=conversation_id, user="test_user_thinesh")
# #         print("Delete Conversation Response:")
# #         print(json.dumps(response, indent=2))
# #     except Exception as e:
# #         print(f"Error in delete_conversation test: {str(e)}")
# #         if isinstance(e, requests.HTTPError) and e.response is not None:
# #             print(f"HTTP Error Details: {e.response.text}")

# # def test_rename_conversation(conversation_id: str):
# #     """
# #     Test the rename_conversation method.
# #     """
# #     if not conversation_id:
# #         print("Warning: No valid conversation_id provided. Skipping rename_conversation test.")
# #         return
# #     try:
# #         app = AIApplicationApp()
# #         response = app.rename_conversation(
# #             conversation_id=conversation_id,
# #             user="test_user_thinesh",
# #             name="Renamed Conversation"
# #         )
# #         print("Rename Conversation Response:")
# #         print(json.dumps(response.to_dict(), indent=2))
# #     except Exception as e:
# #         print(f"Error in rename_conversation test: {str(e)}")
# #         if isinstance(e, requests.HTTPError) and e.response is not None:
# #             print(f"HTTP Error Details: {e.response.text}")

# # if __name__ == "__main__":
# #     print("Testing chat_message")
# #     print("-" * 40)
# #     message_id, conversation_id = test_chat_message()
# #     test_message_id = message_id 
# #     test_conversation_id = conversation_id 
# #     print("\nTesting chat_message_streaming and stop_generate_message")
# #     print("-" * 40)
# #     stop_result = test_chat_message_streaming()
# #     print("\nTesting get_conversation_messages")
# #     print("-" * 40)
# #     test_get_conversation_messages(test_conversation_id)
# #     print("\nTesting get_conversations")
# #     print("-" * 40)
# #     test_get_conversations()
# #     # print("\nTesting get_suggested_messages")
# #     # print("-" * 40)
# #     # test_get_suggested_messages(test_message_id)
# #     print("\nTesting send_message_feedback")
# #     print("-" * 40)
# #     test_send_message_feedback(test_message_id)
# #     print("\nTesting rename_conversation")
# #     print("-" * 40)
# #     test_rename_conversation(test_conversation_id)
# #     # print("\nTesting delete_conversation")
# #     # print("-" * 40)
# #     # test_delete_conversation(test_conversation_id)




# # import requests
# # import json

# # API_KEY = "app-FHBylBZuiIBO3AeGQNlsiW7p"
# # BASE_URL = "https://copilot-dev.sifymdp.digital/v1/chat-messages"

# # payload = {
# #     "inputs": {},
# #     "query": "i want to deploy graphmate from appfoundry",
# #     "response_mode": "streaming",
# #     "conversation_id": "",
# #     "user": "abc-123",
# #     "files": [
# #     ]
# # }

# # headers = {
# #     "Authorization": f"Bearer {API_KEY}",
# #     "Content-Type": "application/json"
# # }

# # response = requests.post(BASE_URL, headers=headers, json=payload, stream=True)

# # for line in response.iter_lines():
# #     if line:
# #         # Remove "data:" prefix if present
# #         decoded = line.decode()
# #         if decoded.startswith("data:"):
# #             decoded = decoded[len("data:"):].strip()
# #         try:
# #             chunk = json.loads(decoded)
# #             # Print the answer as it streams
# #             if "answer" in chunk and chunk["answer"]:
# #                 print(chunk["answer"], end="", flush=True)
# #             # Optionally print agent thoughts if present
# #             if "metadata" in chunk and chunk["metadata"]:
# #                 agent_thoughts = chunk["metadata"].get("agent_thoughts")
# #                 if agent_thoughts:
# #                     print("\nAgent Thoughts:", agent_thoughts)
# #         except Exception:
# #             continue



from sify.aiplatform.aistudio.app import AIApplication

# Set your new base URL and API key
app = AIApplication(
    base_url="https://copilot-dev.sifymdp.digital/v1",
    api_key="app-GhZgLCBeON9837QdRvAIUiSF"
)

def simple_test():
    try:
        response = app.chat_message(
            query="Hi thinesh",
            user="test_user",
            response_mode="blocking"
        )
        print("AI Response:", response.answer)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    simple_test()