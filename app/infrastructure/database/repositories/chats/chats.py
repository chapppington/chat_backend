from dataclasses import dataclass

from infrastructure.database.converters.chats.chats import (
    chat_document_to_entity,
    chat_entity_to_document,
)
from infrastructure.database.repositories.base.mongo import BaseMongoDBRepository

from domain.chats.entities.chats import ChatEntity
from domain.chats.interfaces.repository import BaseChatsRepository


@dataclass
class MongoDBChatsRepository(BaseChatsRepository, BaseMongoDBRepository):
    async def get_chat_by_oid(self, oid: str) -> ChatEntity | None:
        chat_document = await self._collection.find_one(filter={"oid": oid})

        if not chat_document:
            return None

        return chat_document_to_entity(chat_document)

    async def check_chat_exists_by_title(self, title: str) -> bool:
        return bool(await self._collection.find_one(filter={"title": title}))

    async def add_chat(self, chat: ChatEntity) -> None:
        await self._collection.insert_one(chat_entity_to_document(chat))

    async def delete_chat_by_oid(self, chat_oid: str) -> None:
        await self._collection.delete_one(filter={"oid": chat_oid})
