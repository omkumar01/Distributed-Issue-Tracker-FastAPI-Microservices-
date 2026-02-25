"""
WebSocket endpoints for real-time comment updates.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
from uuid import UUID
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter()

class ConnectionManager:
    """Manages active WebSocket connections per issue."""
    def __init__(self):
        # Maps issue_id to a list of active websocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, issue_id: str):
        await websocket.accept()
        if issue_id not in self.active_connections:
            self.active_connections[issue_id] = []
        self.active_connections[issue_id].append(websocket)
        logger.info(f"Client connected to issue {issue_id}")

    def disconnect(self, websocket: WebSocket, issue_id: str):
        if issue_id in self.active_connections:
            if websocket in self.active_connections[issue_id]:
                self.active_connections[issue_id].remove(websocket)
            if not self.active_connections[issue_id]:
                del self.active_connections[issue_id]
        logger.info(f"Client disconnected from issue {issue_id}")

    async def broadcast(self, issue_id: str, message: dict):
        """Broadcast a message to all clients listening to a specific issue."""
        if issue_id in self.active_connections:
            dead_connections = []
            for connection in self.active_connections[issue_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to client: {e}")
                    dead_connections.append(connection)
            
            # Clean up dead connections
            for connection in dead_connections:
                self.disconnect(connection, issue_id)

# Singleton manager
manager = ConnectionManager()

@router.websocket("/issue/{issue_id}")
async def websocket_issue_comments(websocket: WebSocket, issue_id: UUID):
    """
    WebSocket endpoint for a specific issue.
    Clients connect here to receive real-time updates for comments on this issue.
    """
    issue_id_str = str(issue_id)
    await manager.connect(websocket, issue_id_str)
    try:
        while True:
            # We expect clients to mostly listen, but they could send ping/pong
            data = await websocket.receive_text()
            # Echo back or handle if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket, issue_id_str)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, issue_id_str)
