from typing import List, Dict, Any, Set
from fastapi import WebSocket
from app.core.logging import logger


class NotificationService:
    """
    Manages active WebSocket connections and broadcasts real-time telemetry,
    sensor alerts, and risk updates to officer dashboards and field interfaces.
    """

    def __init__(self):
        self._active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self._active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total active: {len(self._active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self._active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total active: {len(self._active_connections)}")

    async def broadcast(self, event_type: str, data: Dict[str, Any]):
        """
        Broadcast JSON payload to all connected clients.
        """
        if not self._active_connections:
            return

        payload = {
            "event": event_type,
            "data": data
        }

        stale = []
        for connection in self._active_connections:
            try:
                await connection.send_json(payload)
            except Exception as e:
                logger.warning(f"Error sending message to WebSocket client: {e}")
                stale.append(connection)

        for s in stale:
            self._active_connections.discard(s)


notification_service = NotificationService()
