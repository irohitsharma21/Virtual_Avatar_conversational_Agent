import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
import logging
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentServer, AgentSession, JobContext, cli, Agent
from livekit.plugins import anam, google, deepgram, silero

# Load environment variables
load_dotenv()

# We need GOOGLE_API_KEY for Gemini. If GEMINI_API_KEY is present, set GOOGLE_API_KEY to it.
if "GEMINI_API_KEY" in os.environ and "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

# Initialize the server
server = AgentServer()

@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):
    logging.info(f"Starting agent job in room: {ctx.room.name}")

    # Connect to the LiveKit room
    await ctx.connect()
    logging.info(f"Connected to room: {ctx.room.name}")

    # Instantiate the voice pipeline components
    stt_instance = deepgram.STT()
    llm_instance = google.LLM(model="gemini-2.5-flash")
    tts_instance = deepgram.TTS()
    vad_instance = silero.VAD.load()

    # Create the agent logic object
    agent = Agent(
        instructions="You are Cara, a helpful customer service representative. Keep your answers brief and concise.",
        stt=stt_instance,
        llm=llm_instance,
        tts=tts_instance,
        vad=vad_instance,
    )

    # Initialize the AgentSession
    session = AgentSession(
        stt=stt_instance,
        llm=llm_instance,
        tts=tts_instance,
        vad=vad_instance,
    )

    # Configure the Anam Avatar Session
    avatar_id = os.getenv("ANAM_AVATAR_ID", "30fa96d0-26c4-4e55-94a0-517025942e18")
    avatar = anam.AvatarSession(
        persona_config=anam.PersonaConfig(
            name="Cara",
            avatarId=avatar_id,
        ),
        api_key=os.getenv("ANAM_API_KEY"),
    )

    # Start the avatar and wait for it to join the room
    logging.info("Starting Anam Avatar Session...")
    await avatar.start(session, room=ctx.room)
    logging.info("Anam Avatar Session started and joined the room.")

    # Start the agent session with the user
    logging.info("Starting Agent Session...")
    await session.start(room=ctx.room, agent=agent)
    logging.info("Agent Session started successfully.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cli.run_app(server)
