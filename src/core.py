from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import AutoSubscribe, JobContext, llm, multimodal

from .config import model
from .functions.tools import AssistantFunctions

load_dotenv(dotenv_path=".env.local")

async def entrypoint(ctx: JobContext):
    print(f"Connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    participant = await ctx.wait_for_participant()
    run_multimodal_agent(ctx, participant)
    print("Agent started")

def run_multimodal_agent(ctx: JobContext, participant: rtc.RemoteParticipant):
    print("Starting multimodal agent")
    
    agent = multimodal.MultimodalAgent(
        model=model.create_model(),
        chat_ctx=llm.ChatContext(),
        fnc_ctx=AssistantFunctions(),
    )
    
    agent.start(ctx.room, participant)
    agent.generate_reply() 