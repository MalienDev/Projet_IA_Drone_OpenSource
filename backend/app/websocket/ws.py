"""
WebSocket endpoint for real-time alerts.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from .manager import manager

router = APIRouter()


@router.websocket("/ws/alerts")
async def websocket_alerts(
    websocket: WebSocket,
    client_id: str = Query(..., description="Unique client identifier")
):
    """
    WebSocket endpoint for real-time alert updates.

    Clients connect to this endpoint to receive alerts as they are published
    to the Redis alert channel by the rules engine.

    Args:
        websocket: WebSocket connection
        client_id: Unique identifier for the client (required query parameter)
    """
    await manager.connect(websocket, client_id)

    try:
        # Keep the connection alive and listen for client messages (if any)
        while True:
            # Receive any messages from the client (e.g., ping/pong)
            data = await websocket.receive_text()
            # Echo back or handle client messages if needed
            # For now, we just ignore client messages
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"Client {client_id} disconnected")
    except Exception as e:
        manager.disconnect(websocket)
        print(f"WebSocket error for client {client_id}: {e}")
