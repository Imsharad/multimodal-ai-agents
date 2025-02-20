import sys
from pathlib import Path
from livekit.agents import cli

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent))

from src.agent import entrypoint

if __name__ == "__main__":
    cli.run_app(
        cli.WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )
