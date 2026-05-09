from google.adk import Agent
from my_agent.config import MODEL
from my_agent.tools.pubsub import inject_pubsub_notes

orchestrator_agent = Agent(
    name="orchestrator_agent",
    model=MODEL,
    instruction="""You are the orchestrator for the logistics workflow.

    System notes (from Pub/Sub): {pubsub_notes}

    Decide how to handle the user's request:
    - If it's simple conversation, respond directly in natural language.
    - If it needs a specialist, output ONLY the routing keyword and query:
      DATABASE: <user query>
      WEATHER: <user query>
      SEARCH: <user query>
    """,
    before_agent_callback=inject_pubsub_notes,
    output_key="routing_decision",
)
