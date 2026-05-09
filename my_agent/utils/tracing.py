"""OpenTelemetry tracing helpers for the logistics agent.

Tracing is enabled when OTEL_EXPORTER_OTLP_ENDPOINT is set in the environment.
If the env var is absent, a no-op tracer is used so the app runs without any
tracing infrastructure.

Usage:
    from my_agent.utils.tracing import get_tracer

    tracer = get_tracer(__name__)

    with tracer.start_as_current_span("my_operation") as span:
        span.set_attribute("key", "value")
        ...
"""
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

_initialized = False


def _init_tracing() -> None:
    global _initialized
    if _initialized:
        return

    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        # No exporter configured — use no-op tracer
        _initialized = True
        return

    try:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    except ImportError:
        # Package not installed — fall back to no-op tracer silently
        _initialized = True
        return

    resource = Resource.create({SERVICE_NAME: os.getenv("OTEL_SERVICE_NAME", "logistics-agent")})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True))
    )
    trace.set_tracer_provider(provider)
    _initialized = True


def get_tracer(name: str) -> trace.Tracer:
    """Returns an OpenTelemetry tracer for the given module name."""
    _init_tracing()
    return trace.get_tracer(name)
