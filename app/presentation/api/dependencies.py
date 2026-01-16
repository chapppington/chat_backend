from uuid import UUID

from fastapi import (
    Depends,
    HTTPException,
    Request,
    status,
    WebSocketException,
)
from fastapi.websockets import WebSocket

from presentation.api.auth import auth_service


async def get_refresh_token_payload(
    request: Request,
) -> dict:
    """Dependency для получения payload из refresh токена."""
    return await auth_service.refresh_token_required(request)


async def get_access_token_payload(
    request: Request,
) -> dict:
    """Dependency для получения payload из access токена."""
    return await auth_service.access_token_required(request)


async def get_current_user_id(
    token_payload: dict = Depends(get_access_token_payload),
) -> UUID:
    """Dependency для получения текущего user_id из токена."""
    user_id_str = token_payload.sub
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token payload",
        )
    try:
        return UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format in token",
        )


async def get_access_token_payload_from_websocket(
    websocket: WebSocket,
) -> dict:
    """Dependency для получения payload из access токена для WebSocket."""
    try:
        # Создаем Request-like объект из WebSocket для auth_service
        # authx работает с cookies и headers из WebSocket
        class WebSocketRequest:
            def __init__(self, ws: WebSocket):
                self.cookies = ws.cookies
                # Преобразуем headers из WebSocket в формат, который ожидает authx
                self.headers = ws.headers

        ws_request = WebSocketRequest(websocket)
        return await auth_service.access_token_required(ws_request)
    except Exception as e:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason=f"Authentication failed: {str(e)}",
        )


async def get_current_user_id_from_websocket(
    token_payload: dict = Depends(get_access_token_payload_from_websocket),
) -> UUID:
    """Dependency для получения текущего user_id из токена для WebSocket."""
    user_id_str = token_payload.sub
    if not user_id_str:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="User ID not found in token payload",
        )
    try:
        return UUID(user_id_str)
    except ValueError:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid user ID format in token",
        )
