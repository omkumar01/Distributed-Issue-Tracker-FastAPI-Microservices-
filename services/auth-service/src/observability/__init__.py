"""OpenTelemetry integration for observability."""

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)


def init_tracing():
    """Initialize OpenTelemetry tracing."""
    if not settings.JAEGER_ENABLED:
        logger.info("Jaeger tracing disabled")
        return
    
    try:
        jaeger_exporter = JaegerExporter(
            agent_host_name=settings.JAEGER_HOST,
            agent_port=settings.JAEGER_PORT,
        )
        
        trace_provider = TracerProvider(
            resource=Resource.create({SERVICE_NAME: settings.SERVICE_NAME})
        )
        trace_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
        trace.set_tracer_provider(trace_provider)
        
        logger.info("Jaeger tracing initialized")
    except Exception as e:
        logger.error(f"Failed to initialize tracing: {e}")


def init_fastapi_instrumentation(app):
    """Instrument FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    try:
        FastAPIInstrumentor.instrument_app(app)
        logger.info("FastAPI instrumentation initialized")
    except Exception as e:
        logger.error(f"Failed to instrument FastAPI: {e}")


def init_sqlalchemy_instrumentation():
    """Instrument SQLAlchemy."""
    try:
        SQLAlchemyInstrumentor().instrument()
        logger.info("SQLAlchemy instrumentation initialized")
    except Exception as e:
        logger.error(f"Failed to instrument SQLAlchemy: {e}")
