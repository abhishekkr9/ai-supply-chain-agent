from google.adk import Workflow
from my_agent.agents.orchestrator import orchestrator_agent
from my_agent.agents.specialists import (
    database_specialist_agent,
    weather_agent,
    search_specialist_agent,
)
from my_agent.agents.validator import validator_agent
from my_agent.agents.responder import responder_agent
from my_agent.agents.human_in_loop import human_in_loop_agent
from my_agent.routers.routing import router
from my_agent.routers.validation import validation_router

root_agent = Workflow(
    name="routing_workflow",
    edges=[
        ("START", orchestrator_agent),
        (orchestrator_agent, router),
        (
            router,
            {
                "DATABASE": database_specialist_agent,
                "WEATHER":  weather_agent,
                "SEARCH":   search_specialist_agent,
            },
        ),
        (database_specialist_agent, validator_agent),
        (weather_agent,    validator_agent),
        (search_specialist_agent,   validator_agent),
        (validator_agent, validation_router),
        (
            validation_router,
            {
                "APPROVED": responder_agent,
                "REJECTED": human_in_loop_agent,
            },
        ),
    ],
)
