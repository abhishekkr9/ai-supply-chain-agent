from google.genai import types
from google.adk import Agent
from google.adk.tools import google_search
from my_agent.config import MODEL
from my_agent.tools.database import cloud_sql_toolset
from my_agent.tools.weather import fetch_weather

database_specialist_agent = Agent(
    name="database_specialist_agent",
    model=MODEL,
    instruction="""You are a Database Specialist Agent for the logistics system.
    Your job is to query the database and answer the user's question.

    Database schema:
    - Table: Locations (location_id, name, facility_type, city, state_province, latitude, longitude)
    - Table: Shipments (shipment_id, tracking_number, origin_id, destination_id, status, carrier,
                        current_lat, current_lon, departure_time, estimated_arrival)

    NOTE: To get origin/destination city names or coordinates, JOIN Shipments to Locations
    using origin_id or destination_id.

    OUTPUT RULES — follow these exactly:
    - Output ONE sentence or short paragraph that directly answers the user's question.
    - Do NOT include the SQL query in your output under any circumstances.
    - Do NOT include section headers like "SQL Query:", "Database Result:", or "Summary:".
    - Do NOT include raw table data, column names, or markdown tables.
    - Write in plain English as if speaking directly to the user.""",
    tools=[cloud_sql_toolset],
    output_key="specialist_response",
)

weather_agent = Agent(
    name="weather_agent",
    model=MODEL,
    instruction="""You are an Intelligence Specialist Agent.
    Your job is to check external conditions (weather, traffic, geopolitical events)
    that may affect a shipment route. Use the fetch_weather tool to get real-time
    weather data for the relevant locations.

    Return a concise alert summarizing any risks to the route.""",
    tools=[fetch_weather],
    output_key="specialist_response",
)

search_specialist_agent = Agent(
    name="search_specialist_agent",
    model=MODEL,
    instruction="""You are a web research fallback agent.
    Use Google Search to answer requests that are not shipment database lookups
    and not route-intelligence checks. Prefer concise, factual answers and cite
    sources when the grounding response provides them.""",
    tools=[google_search],
    generate_content_config=types.GenerateContentConfig(
        tool_config=types.ToolConfig(include_server_side_tool_invocations=True)
    ),
    output_key="specialist_response",
)
