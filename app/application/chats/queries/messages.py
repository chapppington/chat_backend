from dataclasses import dataclass
from typing import Iterable
from uuid import UUID

from application.base.query import (
    BaseQuery,
    BaseQueryHandler,
)
from domain.chats.entities.messages import MessageEntity
from domain.chats.filters.messages import GetMessagesFilters
from domain.chats.interfaces.repository import BaseMessagesRepository


@dataclass(frozen=True)
class GetMessagesQuery(BaseQuery):
    chat_id: UUID
    limit: int = 10
    offset: int = 0


@dataclass(frozen=True)
class GetMessagesQueryHandler(
    BaseQueryHandler[GetMessagesQuery, tuple[Iterable[MessageEntity], int]],
):
    messages_repository: BaseMessagesRepository

    async def handle(
        self,
        query: GetMessagesQuery,
    ) -> tuple[Iterable[MessageEntity], int]:
        filters = GetMessagesFilters(
            limit=query.limit,
            offset=query.offset,
        )

        return await self.messages_repository.get_messages(
            chat_id=query.chat_id,
            filters=filters,
        )
