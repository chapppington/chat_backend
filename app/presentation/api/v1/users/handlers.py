from io import BytesIO
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    status,
)

from presentation.api.dependencies import get_current_user_id
from presentation.api.schemas import (
    ApiResponse,
    ErrorResponseSchema,
)
from presentation.api.v1.users.schemas import UserResponseSchema

from application.container import init_container
from application.mediator import Mediator
from application.users.commands import UploadAvatarCommand
from application.users.queries import GetUserByIdQuery


router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[UserResponseSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[UserResponseSchema]},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema},
    },
)
async def get_current_user(
    user_id: UUID = Depends(get_current_user_id),
    container=Depends(init_container),
) -> ApiResponse[UserResponseSchema]:
    """Получение информации о текущем пользователе."""
    mediator: Mediator = container.resolve(Mediator)

    query = GetUserByIdQuery(user_id=user_id)
    user = await mediator.handle_query(query)

    return ApiResponse[UserResponseSchema](
        data=UserResponseSchema.from_entity(user),
    )


@router.post(
    "/avatar",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[UserResponseSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[UserResponseSchema]},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponseSchema},
    },
)
async def upload_avatar(
    file: UploadFile = File(...),
    user_id: UUID = Depends(get_current_user_id),
    container=Depends(init_container),
) -> ApiResponse[UserResponseSchema]:
    """Загрузка аватара пользователя."""
    mediator: Mediator = container.resolve(Mediator)

    # Read file content into BytesIO
    file_content = await file.read()
    file_obj = BytesIO(file_content)
    file_obj.seek(0)  # Reset file pointer to beginning

    command = UploadAvatarCommand(
        user_id=user_id,
        file_obj=file_obj,
        filename=file.filename or "avatar",
    )

    user, *_ = await mediator.handle_command(command)

    return ApiResponse[UserResponseSchema](
        data=UserResponseSchema.from_entity(user),
    )
