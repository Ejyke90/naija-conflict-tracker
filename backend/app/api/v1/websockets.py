"""WebSocket monitoring endpoint for real-time pipeline status"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.websockets import get_monitoring_manager, ConnectionManager
from app.api.v1.endpoints.monitoring import get_pipeline_status_data
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

# Configuration
BROADCAST_INTERVAL = 5  # seconds - broadcast pipeline status every 5 seconds
MAX_CONNECTIONS = 100


@router.websocket("/ws/monitoring/pipeline-status")
async def websocket_pipeline_monitoring(
    websocket: WebSocket,
    manager: ConnectionManager = Depends(get_monitoring_manager)
):
    """WebSocket endpoint for real-time pipeline status updates
    
    Clients connecting here will receive pipeline status updates every 5 seconds.
    Automatically falls back to polling if connection fails.
    
    Example client code:
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/ws/monitoring/pipeline-status');
    ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      console.log('Pipeline status:', update.data);
    };
    ```
    """
    
    # Check connection limit
    if manager.get_connection_count() >= MAX_CONNECTIONS:
        await websocket.close(code=1008, reason="Max connections exceeded")
        return
    
    # Connect the client
    await manager.connect(websocket)
    
    try:
        # Get database session for monitoring
        from app.db.database import SessionLocal
        
        # Keep connection alive and periodically send updates
        while True:
            try:
                # Wait for client message (with timeout for keep-alive)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                # Clients can send any message to keep connection alive
                # Could implement custom commands here in the future
                logger.debug(f"Received message from client: {data}")
                
            except asyncio.TimeoutError:
                # Timeout is normal - just continue (keep-alive)
                pass
            
            except WebSocketDisconnect:
                logger.info("Client disconnected normally")
                await manager.disconnect(websocket)
                break
            
            except Exception as e:
                logger.error(f"Error receiving from WebSocket: {str(e)}")
                await manager.disconnect(websocket)
                break
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
        await manager.disconnect(websocket)


async def broadcast_pipeline_updates():
    """Background task to broadcast pipeline status updates
    
    This should be called from the application startup to continuously
    monitor the pipeline and broadcast updates to all connected clients.
    """
    from app.db.database import SessionLocal
    from app.websockets import monitoring_manager
    
    while True:
        try:
            # Wait for broadcast interval
            await asyncio.sleep(BROADCAST_INTERVAL)
            
            # Skip if no clients connected
            if monitoring_manager.get_connection_count() == 0:
                continue
            
            # Get fresh pipeline status
            db = SessionLocal()
            try:
                status_data = await get_pipeline_status_data(db)
                await monitoring_manager.broadcast(status_data)
            finally:
                db.close()
        
        except Exception as e:
            logger.error(f"Error in broadcast task: {str(e)}")
            await asyncio.sleep(1)  # Brief pause before retry
