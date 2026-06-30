"""
WebSocket endpoint for real-time alerts.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status, HTTPException
from .manager import manager
from app.auth.dependencies import get_current_user_ws
from app.db.base import SessionLocal
from app.models.operator import Operator

router = APIRouter()


@router.websocket("/ws/alerts")
async def websocket_alerts(
    websocket: WebSocket,
    token: str = Query(..., description="JWT authentication token")
):
    """
    WebSocket endpoint for real-time alert updates.

    Clients connect to this endpoint to receive alerts as they are published
    to the Redis alert channel by the rules engine.

    Args:
        websocket: WebSocket connection
        token: JWT authentication token (required query parameter)
    """
    # Validate JWT token
    db = SessionLocal()
    try:
        user: Operator = await get_current_user_ws(token, db)
    except HTTPException as e:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        print(f"WebSocket connection rejected: invalid token - {e.detail}")
        return
    except Exception as e:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        print(f"WebSocket connection rejected: invalid token - {e}")
        return
    finally:
        db.close()

    client_id = f"{user.username}_{id(websocket)}"
    await manager.connect(websocket, client_id)
    print(f"Client {client_id} connected (user: {user.username})")

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
