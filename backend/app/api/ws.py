from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Set

router = APIRouter()

active_connections: Set[WebSocket] = set()


@router.websocket("/events")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast to all connected clients
            for conn in active_connections:
                try:
                    await conn.send_text(data)
                except Exception:
                    pass
    except WebSocketDisconnect:
        active_connections.discard(websocket)


@router.websocket("/scan-logs")
async def scan_logs_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass


async def broadcast_event(event_type: str, payload: dict):
    import json
    message = json.dumps({"type": event_type, "data": payload})
    dead_connections = set()
    for conn in active_connections:
        try:
            await conn.send_text(message)
        except Exception:
            dead_connections.add(conn)
    active_connections -= dead_connections