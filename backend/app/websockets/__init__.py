"""WebSocket connection manager for real-time pipeline status broadcasting"""

from typing import Set
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts pipeline status updates"""
    
    def __init__(self):
        """Initialize connection manager with empty connection set"""
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"✅ WebSocket connected. Active connections: {len(self.active_connections)}")
    
    async def disconnect(self, websocket: WebSocket):
        """Remove client from active connections"""
        self.active_connections.discard(websocket)
        logger.info(f"❌ WebSocket disconnected. Active connections: {len(self.active_connections)}")
    
    async def broadcast(self, data: dict):
        """Broadcast message to all connected clients
        
        Args:
            data: Dictionary containing pipeline status to broadcast
        """
        if not self.active_connections:
            return  # No clients connected
        
        message = json.dumps({
            "type": "pipeline_status_update",
            "data": data
        })
        
        # Track failed connections for cleanup
        disconnected = []
        
        for websocket in self.active_connections:
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.warning(f"⚠️  Failed to send to client: {str(e)}")
                disconnected.append(websocket)
        
        # Clean up disconnected clients
        for ws in disconnected:
            await self.disconnect(ws)
    
    def get_connection_count(self) -> int:
        """Get current number of active WebSocket connections"""
        return len(self.active_connections)


# Global connection manager instance
monitoring_manager = ConnectionManager()


async def get_monitoring_manager() -> ConnectionManager:
    """Dependency injection for connection manager"""
    return monitoring_manager
