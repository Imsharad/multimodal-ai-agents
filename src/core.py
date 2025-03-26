from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import AutoSubscribe, JobContext, llm, multimodal
import atexit
import asyncio

from .config import model
from .functions.unified_tools import UnifiedFunctions

load_dotenv(dotenv_path=".env.local")

# Global variable to store the function context for cleanup
_function_context = None

def cleanup_resources():
    """Cleanup resources on exit"""
    if _function_context:
        # Create a new event loop for the cleanup task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Run cleanup in the new loop
            loop.run_until_complete(_function_context.cleanup())
        finally:
            loop.close()
        print("Cleaned up resources")

# Register the cleanup function to be called on exit
atexit.register(cleanup_resources)

async def entrypoint(ctx: JobContext):
    global _function_context
    
    print(f"Connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    participant = await ctx.wait_for_participant()
    
    # Create model-agnostic components
    chat_ctx = llm.ChatContext()
    fnc_ctx = UnifiedFunctions()
    
    # Store function context for cleanup
    _function_context = fnc_ctx
    
    # Create the agent with selected model
    agent = multimodal.MultimodalAgent(
        model=model.create_model(),
        chat_ctx=chat_ctx,
        fnc_ctx=fnc_ctx,
    )
    
    agent.start(ctx.room, participant)
    agent.generate_reply()
    print("Agent started") 