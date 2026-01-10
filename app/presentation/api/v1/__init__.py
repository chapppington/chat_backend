from fastapi import APIRouter

from presentation.api.v1.auth.handlers import router as auth_router
from presentation.api.v1.users.handlers import router as users_router


v1_router = APIRouter()

v1_router.include_router(auth_router)
v1_router.include_router(users_router)
