from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)

from infrastructure.websockets.manager import BaseConnectionManager
from presentation.api.dependencies import get_current_user_id
from presentation.api.schemas import (
    ApiResponse,
    ErrorResponseSchema,
)
from presentation.api.v1.chats.schemas import (
    ChatResponseSchema,
    CreateChatRequestSchema,
    CreateMessageRequestSchema,
    MessageResponseSchema,
    MessagesListResponseSchema,
)

from application.chats.commands import (
    CreateChatCommand,
    CreateMessageCommand,
    DeleteChatCommand,
)
from application.chats.queries import (
    GetChatByIdQuery,
    GetMessagesQuery,
)
from application.container import init_container
from application.mediator import Mediator


router = APIRouter(prefix="/chats", tags=["chats"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[ChatResponseSchema],
    responses={
        status.HTTP_201_CREATED: {"model": ApiResponse[ChatResponseSchema]},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
        status.HTTP_409_CONFLICT: {"model": ErrorResponseSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponseSchema},
    },
)
async def create_chat(
    request: CreateChatRequestSchema,
    owner_id: UUID = Depends(get_current_user_id),
    container=Depends(init_container),
) -> ApiResponse[ChatResponseSchema]:
    """Создание нового чата."""
    mediator: Mediator = container.resolve(Mediator)
    command = CreateChatCommand(
        title=request.title,
        owner_id=owner_id,
    )

    chat, *_ = await mediator.handle_command(command)

    return ApiResponse[ChatResponseSchema](
        data=ChatResponseSchema.from_entity(chat),
    )


@router.get(
    "/{chat_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[ChatResponseSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[ChatResponseSchema]},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponseSchema},
    },
)
async def get_chat_by_id(
    chat_id: UUID,
    container=Depends(init_container),
) -> ApiResponse[ChatResponseSchema]:
    """Получение чата по ID."""
    mediator: Mediator = container.resolve(Mediator)

    query = GetChatByIdQuery(chat_id=chat_id)
    chat = await mediator.handle_query(query)

    return ApiResponse[ChatResponseSchema](
        data=ChatResponseSchema.from_entity(chat),
    )


@router.delete(
    "/{chat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponseSchema},
    },
)
async def delete_chat(
    chat_id: UUID,
    container=Depends(init_container),
) -> None:
    """Удаление чата по ID."""
    mediator: Mediator = container.resolve(Mediator)

    command = DeleteChatCommand(chat_id=chat_id)
    await mediator.handle_command(command)


@router.post(
    "/{chat_id}/messages",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[MessageResponseSchema],
    responses={
        status.HTTP_201_CREATED: {"model": ApiResponse[MessageResponseSchema]},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponseSchema},
    },
)
async def create_message(
    chat_id: UUID,
    request: CreateMessageRequestSchema,
    sender_id: UUID = Depends(get_current_user_id),
    container=Depends(init_container),
) -> ApiResponse[MessageResponseSchema]:
    """Создание нового сообщения в чате."""
    mediator: Mediator = container.resolve(Mediator)
    command = CreateMessageCommand(
        chat_id=chat_id,
        sender_id=sender_id,
        content=request.content,
    )

    message, *_ = await mediator.handle_command(command)
    message_response = MessageResponseSchema.from_entity(message)

    # Отправляем уведомление всем подключенным к чату клиентам через WebSocket
    connection_manager: BaseConnectionManager = container.resolve(BaseConnectionManager)
    await connection_manager.send_json_to_all(
        key=str(chat_id),
        data={
            "type": "new_message",
            "message": message_response.model_dump(mode="json"),
        },
    )

    return ApiResponse[MessageResponseSchema](
        data=message_response,
    )


@router.get(
    "/{chat_id}/messages",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[MessagesListResponseSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[MessagesListResponseSchema]},
    },
)
async def get_messages(
    chat_id: UUID,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    container=Depends(init_container),
) -> ApiResponse[MessagesListResponseSchema]:
    """Получение сообщений чата с пагинацией."""
    mediator: Mediator = container.resolve(Mediator)

    query = GetMessagesQuery(
        chat_id=chat_id,
        limit=limit,
        offset=offset,
    )
    messages, total = await mediator.handle_query(query)

    return ApiResponse[MessagesListResponseSchema](
        data=MessagesListResponseSchema(
            items=[MessageResponseSchema.from_entity(msg) for msg in messages],
            total=total,
        ),
    )
