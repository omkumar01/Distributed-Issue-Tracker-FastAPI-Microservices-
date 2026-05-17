"""Project Service - Main application."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from src.db.database import engine, Base
from src.api.projects import router as projects_router
from src.api.members import router as members_router
from src.api.permissions import router as permissions_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup DB
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Teardown
    await engine.dispose()

app = FastAPI(
    title="Project Service",
    description="Workspace and project management",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(projects_router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(members_router, prefix="/api/v1/projects", tags=["members"])
app.include_router(permissions_router, prefix="/api/v1/projects", tags=["permissions"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "project-service"}

@app.get("/")
async def root():
    return {"message": "Project Service API", "version": "1.0.0"}

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
