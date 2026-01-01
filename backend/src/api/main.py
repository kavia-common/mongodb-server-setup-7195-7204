from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.db import mongodb
from src.api.routes.items import router as items_router

openapi_tags = [
    {
        "name": "health",
        "description": "Service and dependency health checks.",
    },
    {
        "name": "items",
        "description": "CRUD operations for the sample items collection.",
    },
]

app = FastAPI(
    title="FastAPI MongoDB Backend",
    description="FastAPI backend integrating MongoDB via the async Motor driver.",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    """Initialize shared resources (MongoDB client/database) on application startup."""
    mongodb.init()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Gracefully close shared resources (MongoDB client) on application shutdown."""
    await mongodb.close()


@app.get(
    "/health",
    tags=["health"],
    summary="Health check (DB ping)",
    description="Verifies API is running and MongoDB is reachable by issuing a ping command.",
    operation_id="health_check",
)
async def health_check() -> dict:
    """Return service health status and database connectivity state."""
    await mongodb.db.command("ping")
    return {"status": "ok", "mongodb": "ok"}


# Backwards-compatible root route (existing behavior)
@app.get(
    "/",
    tags=["health"],
    summary="Basic health check",
    description="Lightweight health check without a DB ping.",
    operation_id="root_health_check",
)
def root_health_check() -> dict:
    """Return a basic health response without contacting external dependencies."""
    return {"message": "Healthy"}


app.include_router(items_router)
