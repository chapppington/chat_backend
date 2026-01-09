from uuid import UUID

from fastapi import (
    Depends,
    HTTPException,
    Request,
    status,
)

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
