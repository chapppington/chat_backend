from fastapi import APIRouter

from presentation.api.v1.auth.handlers import router as auth_router


v1_router = APIRouter()

v1_router.include_router(auth_router)
