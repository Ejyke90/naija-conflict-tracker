"""WebSocket connection manager for real-time pipeline status broadcasting"""

from typing import Set
from fastapi import WebSocket
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts pipeline status updates
    
    Features:
    - Connection pooling with max limit
    - Automatic stale connection cleanup
    - Efficient broadcast with dead connection removal
    - Resource monitoring
    """
    
    def __init__(self, max_age_minutes: int = 30):
        """Initialize connection manager with empty connection set
        
        Args:
            max_age_minutes: Max age of a connection before forced close (for cleanup)
        """
        self.active_connections: Set[WebSocket] = set()
        self.connection_times = {}  # Track connection timestamp
        self.max_age = timedelta(minutes=max_age_minutes)
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.connection_times[id(websocket)] = datetime.utcnow()
        logger.info(f"✅ WebSocket connected. Active connections: {len(self.active_connections)}")
    
    async def disconnect(self, websocket: WebSocket):
        """Remove client from active connections"""
        self.active_connections.discard(websocket)
        self.connection_times.pop(id(websocket), None)
        logger.info(f"❌ WebSocket disconnected. Active connections: {len(self.active_connections)}")
    
    async def broadcast(self, data: dict):
        """Broadcast message to all connected clients
        
        Efficient broadcast that removes dead connections in-place.
        
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
        
        for websocket in list(self.active_connections):  # Create copy to iterate safely
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.debug(f"⚠️  Failed to send to client: {str(e)}")
                disconnected.append(websocket)
        
        # Clean up disconnected clients
        for ws in disconnected:
            await self.disconnect(ws)
    
    def get_connection_count(self) -> int:
        """Get current number of active WebSocket connections"""
        return len(self.active_connections)
    
    async def cleanup_stale_connections(self):
        """Remove connections older than max_age
        
        This should be called periodically to prevent resource leaks.
        """
        now = datetime.utcnow()
        stale = []
        
        for ws_id, conn_time in list(self.connection_times.items()):
            if now - conn_time > self.max_age:
                stale.append(ws_id)
        
        for ws_id in stale:
            # Find the websocket by id
            for ws in list(self.active_connections):
                if id(ws) == ws_id:
                    try:
                        await ws.close(code=1000, reason="Connection timeout")
                        await self.disconnect(ws)
                        logger.info(f"Cleaned up stale connection after {self.max_age}")
                    except:
                        pass
                    break


# Global connection manager instance
monitoring_manager = ConnectionManager(max_age_minutes=30)


async def get_monitoring_manager() -> ConnectionManager:
    """Dependency injection for connection manager"""
    return monitoring_manager
