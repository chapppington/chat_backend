from uuid import UUID

from fastapi import (
    Depends,
    WebSocketDisconnect,
)
from fastapi.routing import APIRouter
from fastapi.websockets import WebSocket

from infrastructure.websockets.manager import BaseConnectionManager
from presentation.api.dependencies import get_current_user_id_from_websocket

from application.container import init_container


router = APIRouter(
    prefix="/chats",
    tags=["chats"],
)


@router.websocket("/{chat_oid}")
async def websocket_endpoint(
    chat_oid: str,
    websocket: WebSocket,
    user_id: UUID = Depends(get_current_user_id_from_websocket),
):
    """WebSocket endpoint для чата с авторизацией."""
    # Принимаем соединение после успешной авторизации через dependency
    await websocket.accept()

    container = init_container()
    connection_manager: BaseConnectionManager = container.resolve(BaseConnectionManager)
    await connection_manager.accept_connection(websocket=websocket, key=chat_oid)

    await websocket.send_text(f"You are now connected! User ID: {user_id}")

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await connection_manager.remove_connection(websocket=websocket, key=chat_oid)
