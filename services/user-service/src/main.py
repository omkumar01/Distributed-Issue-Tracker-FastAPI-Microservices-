"""User Service - Main application."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging
import os
from contextlib import asynccontextmanager

from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

from src.db.database import engine, Base
from src.api.users import router as users_router
from src.api.teams import router as teams_router
from src.api.roles import router as roles_router
from src.events.consume import start_consumer_thread

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to setup telemetry but fail gracefully if jaeger host not available
try:
    if not trace.get_tracer_provider():
        trace.set_tracer_provider(TracerProvider())
        jaeger_host = os.getenv("JAEGER_AGENT_HOST", "jaeger")
        jaeger_exporter = JaegerExporter(
            agent_host_name=jaeger_host,
            agent_port=6831,
        )
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(jaeger_exporter)
        )
except Exception as e:
    logger.warning(f"Could not initialize OpenTelemetry exporter: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup DB
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Start consumer
    start_consumer_thread()
    
    yield
    # Teardown
    await engine.dispose()

app = FastAPI(
    title="User Service",
    description="User profile and team management",
    version="1.0.0",
    lifespan=lifespan
)

# Instrument the FastAPI app
try:
    FastAPIInstrumentor.instrument_app(app)
except Exception:
    pass

app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(teams_router, prefix="/api/v1/teams", tags=["teams"])
app.include_router(roles_router, prefix="/api/v1/roles", tags=["roles"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "user-service"}

@app.get("/")
async def root():
    return {"message": "User Service API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
