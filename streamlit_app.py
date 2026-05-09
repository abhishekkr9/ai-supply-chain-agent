"""Logistics Agent — Streamlit Chat UI

Run:
    # Terminal 1: start ADK backend
    python main.py

    # Terminal 2: start Streamlit
    streamlit run streamlit_app.py
"""
import json
import time
import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
ADK_BASE_URL = "http://localhost:8000"
APP_NAME     = "my_agent"
USER_ID      = "user"

EXAMPLE_QUERIES = [
    "What is the status of TRK-FLGA-001?",
    "Are there weather alerts on the Miami to Atlanta route?",
    "Show me all delayed shipments.",
    "What carriers are active today?",
]

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Logistics Agent",
    page_icon="🚚",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Session state init
# ---------------------------------------------------------------------------
if "session_id"  not in st.session_state:
    st.session_state.session_id  = None
if "messages"    not in st.session_state:
    st.session_state.messages    = []   # {"role", "content", "notes"?}
if "pending"     not in st.session_state:
    st.session_state.pending     = None # pre-filled query from sidebar


# ---------------------------------------------------------------------------
# ADK helpers
# ---------------------------------------------------------------------------
def create_session() -> str:
    url  = f"{ADK_BASE_URL}/apps/{APP_NAME}/users/{USER_ID}/sessions"
    resp = requests.post(url, json={}, timeout=10)
    resp.raise_for_status()
    return resp.json()["id"]


def _clean_response(text: str) -> str:
    """Strip SQL blocks, raw table sections, and section headers from agent output."""
    import re

    # Remove fenced code blocks (```sql ... ``` or ``` ... ```)
    text = re.sub(r"```[\s\S]*?```", "", text)

    # If the model used section headers, keep only content after "Summary:"
    for marker in ("Summary:", "summary:"):
        if marker in text:
            text = text.split(marker, 1)[1]
            break
    else:
        # No summary marker — strip any "SQL Query:" or "Database Result:" sections
        text = re.sub(
            r"(SQL Query\s*:|Database Result\s*:)[\s\S]*?(?=(Summary:|$))",
            "",
            text,
            flags=re.IGNORECASE,
        )
        # Remove bare SELECT/INSERT/UPDATE/DELETE statements
        text = re.sub(
            r"(?i)^\s*(SELECT|INSERT|UPDATE|DELETE|WITH)[\s\S]*?;",
            "",
            text,
            flags=re.MULTILINE,
        )
        # Remove markdown table rows (lines containing |)
        text = re.sub(r"^\|.*\|\s*$", "", text, flags=re.MULTILINE)
        # Remove table separator lines (e.g. |---|---|)
        text = re.sub(r"^[\|\-\s]+$", "", text, flags=re.MULTILINE)

    return text.strip()


def _stream_response(session_id: str, text: str):
    """Generator that yields text tokens from the ADK SSE stream."""
    url     = f"{ADK_BASE_URL}/run_sse"
    payload = {
        "app_name":    APP_NAME,
        "user_id":     USER_ID,
        "session_id":  session_id,
        "new_message": {"role": "user", "parts": [{"text": text}]},
        "streaming":   False,
    }

    # Collect all candidate text blocks; yield only the last (responder's final output)
    candidate_blocks: list[str] = []
    notes: str | None = None

    with requests.post(url, json=payload, stream=True, timeout=120) as resp:
        resp.raise_for_status()
        for raw_line in resp.iter_lines():
            if not raw_line:
                continue
            line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
            if not line.startswith("data:"):
                continue
            data_str = line[len("data:"):].strip()
            if not data_str or data_str == "[DONE]":
                continue

            try:
                event = json.loads(data_str)
            except json.JSONDecodeError:
                continue

            content = event.get("content", {})
            parts   = content.get("parts", []) if isinstance(content, dict) else []

            # Skip events that contain function calls / tool responses
            if any(isinstance(p, dict) and ("functionCall" in p or "functionResponse" in p) for p in parts):
                continue

            for part in parts:
                token = part.get("text", "") if isinstance(part, dict) else ""
                if not token:
                    continue

                # Skip internal routing tokens and validator verdicts
                stripped = token.strip()
                if stripped in ("PASS", "FAIL", "APPROVED", "REJECTED"):
                    continue
                if any(stripped.startswith(kw) for kw in ("DATABASE:", "WEATHER:", "SEARCH:")):
                    continue

                # Split off system notes block if present
                if "--- System Notes ---" in token:
                    body, _, note_text = token.partition("--- System Notes ---")
                    if body.strip():
                        candidate_blocks.append(body.strip())
                    notes = note_text.strip()
                else:
                    candidate_blocks.append(token)

    # Yield only the last substantive block (the responder's final answer)
    if candidate_blocks:
        final_text = _clean_response(candidate_blocks[-1])
        for word in final_text.split(" "):
            yield word + " "
            time.sleep(0.01)

    # Store notes in session_state so the caller can retrieve them
    st.session_state["_last_notes"] = notes


# ---------------------------------------------------------------------------
# Connect to ADK backend
# ---------------------------------------------------------------------------
if st.session_state.session_id is None:
    try:
        st.session_state.session_id = create_session()
    except Exception as exc:
        st.error(
            f"**Could not connect to the ADK backend at `{ADK_BASE_URL}`.**\n\n"
            f"Make sure `python main.py` (or `adk web`) is running.\n\n"
            f"Error: `{exc}`"
        )
        st.stop()

# ---------------------------------------------------------------------------
# Layout — sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("🚚 Logistics Agent")
    st.caption("Powered by Google ADK + Gemini")

    st.divider()

    st.subheader("Quick Queries")
    for q in EXAMPLE_QUERIES:
        if st.button(q, use_container_width=True):
            st.session_state.pending = q

    st.divider()

    if st.button("🔄 New Session", use_container_width=True):
        st.session_state.session_id = None
        st.session_state.messages   = []
        st.session_state.pending    = None
        st.rerun()

    st.divider()
    st.caption(f"Session: `{st.session_state.session_id}`")
    st.caption(f"Backend: `{ADK_BASE_URL}`")

# ---------------------------------------------------------------------------
# Main area header
# ---------------------------------------------------------------------------
st.header("🚚 Logistics Agent")
st.caption("Ask about shipment status, route conditions, carriers, and more.")
st.divider()

# ---------------------------------------------------------------------------
# Render chat history
# ---------------------------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("notes"):
            with st.expander("📢 System Notes", expanded=False):
                st.info(msg["notes"])

# ---------------------------------------------------------------------------
# Handle input — either typed or from sidebar quick-query
# ---------------------------------------------------------------------------
user_input = st.chat_input("Ask the logistics agent…") or st.session_state.pop("pending", None)

if user_input:
    # Show the user bubble immediately
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    st.session_state["_last_notes"] = None

    # Stream the assistant response
    with st.chat_message("assistant"):
        status = st.status("Thinking…", expanded=False)
        status.write("Routing request to specialist agent…")
        try:
            response_text = st.write_stream(
                _stream_response(st.session_state.session_id, user_input)
            )
            if not response_text:
                response_text = "I couldn't generate a response for that request."
                st.markdown(response_text)
            status.update(label="Done", state="complete", expanded=False)
        except Exception as exc:
            response_text = f"⚠️ Error communicating with the agent: {exc}"
            st.error(response_text)
            status.update(label="Error", state="error")

        notes = st.session_state.pop("_last_notes", None)
        if notes:
            with st.expander("📢 System Notes", expanded=True):
                st.info(notes)

    st.session_state.messages.append({
        "role":    "assistant",
        "content": response_text,
        "notes":   notes,
    })
