from dataclasses import dataclass
from uuid import UUID

from application.base.query import (
    BaseQuery,
    BaseQueryHandler,
)
from domain.chats.entities.chats import ChatEntity
from domain.chats.exceptions.chats import ChatNotFoundException
from domain.chats.interfaces.repository import BaseChatsRepository


@dataclass(frozen=True)
class GetChatByIdQuery(BaseQuery):
    chat_id: UUID


@dataclass(frozen=True)
class GetChatByIdQueryHandler(
    BaseQueryHandler[GetChatByIdQuery, ChatEntity],
):
    chats_repository: BaseChatsRepository

    async def handle(self, query: GetChatByIdQuery) -> ChatEntity:
        chat = await self.chats_repository.get_chat_by_oid(str(query.chat_id))
        if not chat:
            raise ChatNotFoundException(chat_id=query.chat_id)

        return chat
