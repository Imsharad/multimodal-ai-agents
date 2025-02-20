from livekit.plugins.openai import realtime

def create_model():
    return realtime.RealtimeModel(
        voice="alloy",
        temperature=0.8,
        model="gpt-4o-realtime-preview-2024-12-17",
        instructions="You are a helpful assistant. You can use functions to get real-time information. When the user asks about the weather, use the `get_weather` function to fetch the weather information and respond to the user with an audio message containing the weather details. Greet the user and help them with their requests.",
        turn_detection=realtime.ServerVadOptions(
            threshold=0.6, prefix_padding_ms=200, silence_duration_ms=500
        ),
    ) 