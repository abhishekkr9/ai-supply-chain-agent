from google.adk import Event


def router(node_input: str) -> Event:
    """Routes the orchestrator's output to the correct specialist agent."""
    routing_line = ""
    for line in node_input.splitlines():
        stripped = line.strip()
        if stripped:
            routing_line = stripped
            break

    if ":" in routing_line:
        keyword, _ = routing_line.split(":", 1)
        normalized = keyword.strip().upper()
        if normalized in {"DATABASE", "WEATHER", "SEARCH"}:
            return Event(route=[normalized])

    return Event(route=["END"])
