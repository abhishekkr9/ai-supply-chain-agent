from google.adk import Agent
from my_agent.config import MODEL

responder_agent = Agent(
    name="responder_agent",
    model=MODEL,
    instruction="""You are the final responder. Follow these rules strictly.

RULE 1: Always output the specialist response first, exactly as-is:
{specialist_response}

RULE 2: Check the value of pubsub_notes: {pubsub_notes}
- If it is exactly the word 'none' or is empty: stop here, output nothing more.
- If it contains any other text: append the following block exactly:

--- System Notes ---
{pubsub_notes}

Do not summarize, skip, or paraphrase the system notes.""",
)
