"""Entry point for the logistics agent.

Run locally:
    python main.py

Or use the ADK CLI (recommended for development):
    adk web
"""
import os
import uvicorn
from dotenv import load_dotenv

# Load .env from the project root before any agent code is imported
load_dotenv(os.path.join(os.path.dirname(__file__), "my_agent", ".env"))

from my_agent.utils.logging import get_logger

_log = get_logger("main")


def main() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    _log.info("Starting logistics agent server on %s:%d", host, port)

    # Build the ADK ASGI app and serve it with uvicorn
    from google.adk.cli.fast_api import get_fast_api_app

    app = get_fast_api_app(
        agents_dir=os.path.dirname(__file__),
        allow_origins=["*"],
        web=True,
    )

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
