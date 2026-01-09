from fastapi import APIRouter

from presentation.api.v1.user.handlers import router as user_router


v1_router = APIRouter()

v1_router.include_router(user_router)
