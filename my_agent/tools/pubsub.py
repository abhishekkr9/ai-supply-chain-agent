import json
from google.cloud import pubsub_v1
from google.api_core import exceptions as core_exceptions
from google.adk.agents.callback_context import CallbackContext
from my_agent.config import GCP_PROJECT_ID, PUBSUB_SUBSCRIPTION_ID
from my_agent.utils.logging import get_logger
from my_agent.utils.tracing import get_tracer

_log = get_logger(__name__)
_tracer = get_tracer(__name__)

_subscriber = pubsub_v1.SubscriberClient()
_subscription_path = _subscriber.subscription_path(GCP_PROJECT_ID, PUBSUB_SUBSCRIPTION_ID)


def pull_pubsub_notes() -> str:
    """Pulls pending messages from the Pub/Sub subscription and acknowledges them.
    Returns a formatted string of notes, or an empty string if there are none.
    """
    _log.debug("Pulling messages from Pub/Sub subscription: %s", _subscription_path)
    with _tracer.start_as_current_span("pull_pubsub_notes") as span:
        span.set_attribute("pubsub.subscription", _subscription_path)
        try:
            response = _subscriber.pull(
                request={"subscription": _subscription_path, "max_messages": 10},
                timeout=3,
            )
        except core_exceptions.DeadlineExceeded:
            _log.debug("No Pub/Sub messages available (Deadline Exceeded)")
            return ""
        except Exception as e:
            _log.warning("Pub/Sub pull failed: %s", e)
            span.record_exception(e)
            return ""

        if not response.received_messages:
            _log.debug("No Pub/Sub messages available")
            return ""

        notes = []
        ack_ids = []
        for msg in response.received_messages:
            try:
                data = json.loads(msg.message.data.decode("utf-8"))
                event_type = msg.message.attributes.get("event_type", "INFO")
                notes.append(f"[{event_type}] {data.get('payload', {}).get('message', str(data))}")
            except (json.JSONDecodeError, UnicodeDecodeError):
                notes.append(f"[RAW] {msg.message.data!r}")
            ack_ids.append(msg.ack_id)

        _subscriber.acknowledge(
            request={"subscription": _subscription_path, "ack_ids": ack_ids}
        )
        _log.info("Pulled and acknowledged %d Pub/Sub message(s)", len(notes))
        span.set_attribute("pubsub.message_count", len(notes))
        return "\n".join(notes)


def inject_pubsub_notes(callback_context: CallbackContext) -> None:
    """Before-agent callback: pulls Pub/Sub notes and stores them in session state."""
    notes = pull_pubsub_notes()
    callback_context.state["pubsub_notes"] = notes if notes else "none"
    _log.debug("pubsub_notes injected into session state")
