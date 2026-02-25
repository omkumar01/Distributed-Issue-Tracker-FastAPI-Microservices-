"""API Gateway - Entry point for all client requests."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Gateway",
    description="Central entry point for all API requests",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
SERVICE_URLS = {
    "auth": "http://auth-service:8000",
    "users": "http://user-service:8000",
    "projects": "http://project-service:8000",
    "issues": "http://issue-service:8000",
    "comments": "http://comment-service:8000",
    "notifications": "http://notification-service:8000",
    "search": "http://search-service:8000",
    "audit": "http://audit-service:8000",
}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "api-gateway"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Distributed Issue Tracker - API Gateway",
        "version": "1.0.0",
        "services": list(SERVICE_URLS.keys())
    }


@app.get("/services")
async def list_services():
    """List all available services."""
    services = []
    async with httpx.AsyncClient() as client:
        for service_name, url in SERVICE_URLS.items():
            try:
                response = await client.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    services.append({
                        "name": service_name,
                        "status": "healthy",
                        "url": url
                    })
            except Exception as e:
                logger.error(f"Health check failed for {service_name}: {e}")
                services.append({
                    "name": service_name,
                    "status": "unhealthy",
                    "url": url
                })
    
    return {"services": services}


@app.api_route("/api/v1/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway_router(path: str, request):
    """
    Route requests to appropriate services.
    
    Routes:
    - /api/v1/auth/* -> Auth Service
    - /api/v1/users/* -> User Service
    - /api/v1/projects/* -> Project Service
    - /api/v1/issues/* -> Issue Service
    - /api/v1/comments/* -> Comment Service
    - /api/v1/notifications/* -> Notification Service
    - /api/v1/search/* -> Search Service
    - /api/v1/audit/* -> Audit Service
    """
    
    # Extract service name from path
    service_parts = path.split("/")
    if not service_parts:
        raise HTTPException(status_code=400, detail="Invalid path")
    
    service_name = service_parts[0]
    remaining_path = "/".join(service_parts[1:])
    
    # Route to appropriate service
    if service_name not in SERVICE_URLS:
        raise HTTPException(status_code=400, detail=f"Unknown service: {service_name}")
    
    service_url = SERVICE_URLS[service_name]
    target_url = f"{service_url}/api/v1/{remaining_path}"
    
    try:
        async with httpx.AsyncClient() as client:
            # Forward request
            response = await client.request(
                method=request.method,
                url=target_url,
                headers={key: value for key, value in request.headers.items() 
                        if key != "host"},
                content=await request.body() if request.method != "GET" else None,
                timeout=30
            )
            
            return JSONResponse(
                status_code=response.status_code,
                content=response.json() if response.headers.get("content-type") == "application/json" else response.text
            )
    
    except httpx.TimeoutException:
        logger.error(f"Timeout calling {service_name}")
        raise HTTPException(status_code=504, detail=f"Service {service_name} timeout")
    except Exception as e:
        logger.error(f"Error routing to {service_name}: {e}")
        raise HTTPException(status_code=502, detail=f"Bad gateway: {str(e)}")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
