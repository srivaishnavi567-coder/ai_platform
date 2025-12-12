from sify.aiplatform.models.model_as_a_service import ModelAsAService

# Initialize client with Whisper model + API key
client = ModelAsAService(
    model_id="whisper-large-v3-turbo",
    api_key="sk-Vt3QmP2XcJ5wZr7LgD1FaKy9BnR6Us8E"
)

# Example: Audio transcription
try:
    with open("output_speech.mp3", "rb") as audio_file:  # Put an actual wav/mp3 file in your project
        transcription = client.audio_translation(
            file=audio_file,
            model_id="whisper-large-v3-turbo",
            language="en"
        )
        print(f"Transcribed text: {transcription.text}")
except Exception as e:
    print(f"Error in transcription: {e}")