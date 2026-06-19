"""FastAPI application entry point."""

from fastapi import FastAPI, APIRouter
from database import Base, engine
from routers.v1 import tasks, auth


# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Task API with Environment Configuration",
    description="Task CRUD API with Authentication, Authorization, and secrets management via environment variables",
    version="1.0.0"
)

# API v1 router
v1_router = APIRouter(prefix="/v1")
v1_router.include_router(tasks.router)
v1_router.include_router(auth.router)
app.include_router(v1_router)


@app.get("/", tags=["Root"])
def root():
    """Root endpoint."""
    return {
        "message": "Task API with Environment Configuration",
        "version": "1.0.0",
        "endpoints": {
            "tasks": "/v1/tasks",
            "auth": "/v1/auth",
            "docs": "/docs"
        },
        "info": "Configuration via environment variables (.env file). DELETE /v1/tasks/{id} requires ADMIN role"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
