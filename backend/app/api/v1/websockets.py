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
MAX_CONNECTIONS = 50  # Reduced from 100 to prevent resource exhaustion
CONNECTION_TIMEOUT = 60  # seconds before connection is considered dead


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
        
        # Create tasks for two concurrent operations:
        # 1. Listen for client messages (keep-alive signals)
        # 2. Periodically broadcast pipeline status
        
        async def listen_for_messages():
            """Listen for client messages"""
            try:
                while True:
                    # Wait for client message with timeout
                    data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                    logger.debug(f"Received message from client: {data}")
                    
            except asyncio.TimeoutError:
                # Timeout - client may have stalled, let broadcast task handle it
                logger.debug("Receive timeout")
                
            except WebSocketDisconnect:
                logger.info("Client disconnected normally")
                raise
                
            except Exception as e:
                logger.error(f"Error receiving from WebSocket: {str(e)}")
                raise
        
        async def broadcast_status():
            """Periodically broadcast pipeline status"""
            db = SessionLocal()
            try:
                while True:
                    try:
                        # Get current pipeline status
                        status_data = await get_pipeline_status_data(db)
                        
                        # Broadcast to this client
                        message = {
                            "type": "pipeline_status_update",
                            "timestamp": datetime.utcnow().isoformat(),
                            "data": status_data
                        }
                        await websocket.send_json(message)
                        logger.debug(f"Sent pipeline status to client")
                        
                    except Exception as e:
                        logger.error(f"Error broadcasting status: {str(e)}")
                        raise
                    
                    # Wait before next broadcast
                    await asyncio.sleep(BROADCAST_INTERVAL)
                    
            finally:
                db.close()
        
        # Run both tasks concurrently
        # If either fails, the whole connection is closed
        listen_task = asyncio.create_task(listen_for_messages())
        broadcast_task = asyncio.create_task(broadcast_status())
        
        # Wait for either task to complete (one will fail on disconnect)
        done, pending = await asyncio.wait(
            [listen_task, broadcast_task],
            return_when=asyncio.FIRST_EXCEPTION
        )
        
        # Cancel pending tasks
        for task in pending:
            task.cancel()
        
        # Check for exceptions
        for task in done:
            try:
                task.result()
            except Exception:
                pass  # Already logged above
        
        await manager.disconnect(websocket)
    
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
