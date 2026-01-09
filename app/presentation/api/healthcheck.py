from fastapi import (
    APIRouter,
    status,
)

from presentation.api.schemas import (
    ApiResponse,
    PingResponseSchema,
)


healthcheck_router = APIRouter(
    prefix="/healthcheck",
    tags=["healthcheck"],
)


@healthcheck_router.get("", status_code=status.HTTP_200_OK)
async def get_status() -> ApiResponse[PingResponseSchema]:
    return ApiResponse[PingResponseSchema](
        data=PingResponseSchema(result=True),
    )
