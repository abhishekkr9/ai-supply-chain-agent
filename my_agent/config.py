import os

# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------
MODEL = "gemini-3-flash-preview"

# ---------------------------------------------------------------------------
# Logging & Tracing
# ---------------------------------------------------------------------------
# LOG_LEVEL: DEBUG | INFO | WARNING | ERROR  (default: INFO)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# OTEL_EXPORTER_OTLP_ENDPOINT: set to enable OpenTelemetry tracing
# e.g. http://localhost:4317  (gRPC collector)
# Leave unset to run with no-op tracing (zero overhead)
OTEL_SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "logistics-agent")

# ---------------------------------------------------------------------------
# GCP
# ---------------------------------------------------------------------------
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "your-project-id")

# ---------------------------------------------------------------------------
# Pub/Sub
# ---------------------------------------------------------------------------
PUBSUB_SUBSCRIPTION_ID = os.getenv("PUBSUB_SUB_ID", "logistics-orchestrator-sub")

# ---------------------------------------------------------------------------
# Cloud SQL (via Auth Proxy on 127.0.0.1:3306)
# ---------------------------------------------------------------------------
DB_HOST = "127.0.0.1"
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_NAME = os.getenv("DB_NAME", "logistic_db")
