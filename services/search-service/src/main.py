"""Search Service - Main application."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from src.indexers.es_client import async_es_client, init_indices
from src.api.search import router as search_router
from src.consumers.event_consumers import start_consumer_thread

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup ES indices
    try:
        await init_indices()
    except Exception as e:
        logger.error(f"Failed to initialize Elasticsearch indices: {e}")
    
    # Start RabbitMQ consumer
    start_consumer_thread()
    
    yield
    # Teardown
    await async_es_client.close()

app = FastAPI(
    title="Search Service",
    description="Full-text search for issues and comments",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(search_router, prefix="/api/v1/search", tags=["search"])

@app.get("/health")
async def health_check():
    es_status = "unknown"
    try:
        if await async_es_client.ping():
            es_status = "connected"
        else:
            es_status = "disconnected"
    except:
        es_status = "disconnected"

    return {"status": "healthy" if es_status == "connected" else "degraded", "service": "search-service", "elasticsearch": es_status}

@app.get("/")
async def root():
    return {"message": "Search Service API", "version": "1.0.0"}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
