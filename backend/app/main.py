"""
FastAPI application main entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import api_router
from .websocket.ws import router as ws_router
from .websocket.alerts import alert_subscriber
from .services.event_persister import event_persister
import os
import asyncio

app = FastAPI(
    title="Drone Surveillance API",
    description="Backend API for drone surveillance system",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (configure for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

# Include WebSocket routes
app.include_router(ws_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Drone Surveillance API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.on_event("startup")
async def startup_event():
    """Startup event - initialize database connections, etc."""
    print("Starting Drone Surveillance API...")
    # Start the Redis alert subscriber in the background
    asyncio.create_task(alert_subscriber.listen())
    # Start the event persister in the background
    asyncio.create_task(event_persister.listen())


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event - cleanup resources."""
    print("Shutting down Drone Surveillance API...")
    # Stop the Redis alert subscriber
    await alert_subscriber.stop()
    # Stop the event persister
    await event_persister.stop()
