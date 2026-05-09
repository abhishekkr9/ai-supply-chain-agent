import requests
from my_agent.utils.cache import cached
from my_agent.utils.logging import get_logger
from my_agent.utils.tracing import get_tracer

_log = get_logger(__name__)
_tracer = get_tracer(__name__)


@cached(ttl_seconds=300)  # cache weather per location for 5 minutes
def fetch_weather(location: str) -> str:
    """Fetches real-time weather conditions for the given location or route."""
    _log.info("Fetching weather for location: %s", location)
    with _tracer.start_as_current_span("fetch_weather") as span:
        span.set_attribute("weather.location", location)
        try:
            formatted_location = location.replace(' ', '+')
            url = f"https://wttr.in/{formatted_location}?format=%l:+%C,+%t,+Wind:+%w"

            response = requests.get(url, timeout=5)
            response.raise_for_status()
            result = response.text
            _log.info("Weather fetched successfully for: %s", location)
            span.set_attribute("weather.result", result[:200])
            return result

        except requests.exceptions.RequestException as e:
            _log.warning("Weather fetch failed for %s: %s", location, e)
            span.record_exception(e)
            return f"Weather data currently unavailable for {location}."