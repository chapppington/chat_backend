from dataclasses import dataclass
from typing import Iterable
from uuid import UUID

from infrastructure.database.converters.chats.chats import (
    message_document_to_entity,
    message_entity_to_document,
)
from infrastructure.database.repositories.base.mongo import BaseMongoDBRepository

from domain.chats.entities.messages import MessageEntity
from domain.chats.filters.messages import GetMessagesFilters
from domain.chats.interfaces.repository import BaseMessagesRepository


@dataclass
class MongoDBMessagesRepository(BaseMessagesRepository, BaseMongoDBRepository):
    async def add_message(self, message: MessageEntity) -> None:
        await self._collection.insert_one(message_entity_to_document(message))

    async def get_messages(
        self,
        chat_id: UUID,
        filters: GetMessagesFilters,
    ) -> tuple[Iterable[MessageEntity], int]:
        find = {"chat_id": str(chat_id)}

        cursor = self._collection.find(find).limit(filters.limit).skip(filters.offset)

        messages = [message_document_to_entity(message) async for message in cursor]

        total = await self._collection.count_documents(find)

        return messages, total
