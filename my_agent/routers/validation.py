from google.adk import Event


def validation_router(node_input: str) -> Event:
    """Routes validator output to APPROVED or REJECTED path."""
    if node_input.strip().upper() == "PASS":
        return Event(route=["APPROVED"])
    return Event(route=["REJECTED"])
