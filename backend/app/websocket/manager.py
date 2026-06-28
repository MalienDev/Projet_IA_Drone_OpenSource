"""
WebSocket connection manager.
"""

from typing import List, Dict
from fastapi import WebSocket
import json


class ConnectionManager:
    """Manages WebSocket connections for real-time alerts."""

    def __init__(self):
        # Store active connections: {websocket: client_id}
        self.active_connections: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """
        Accept a new WebSocket connection.

        Args:
            websocket: WebSocket connection
            client_id: Unique identifier for the client
        """
        await websocket.accept()
        self.active_connections[websocket] = client_id
        print(f"WebSocket client connected: {client_id}")

    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection.

        Args:
            websocket: WebSocket connection to remove
        """
        client_id = self.active_connections.pop(websocket, None)
        if client_id:
            print(f"WebSocket client disconnected: {client_id}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Send a message to a specific client.

        Args:
            message: Message to send (will be JSON serialized)
            websocket: WebSocket connection to send to
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending message to client: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: dict):
        """
        Broadcast a message to all connected clients.

        Args:
            message: Message to broadcast (will be JSON serialized)
        """
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")
                disconnected.append(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.active_connections)


# Global connection manager instance
manager = ConnectionManager()
