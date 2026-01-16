from dataclasses import (
    dataclass,
    field,
)

from domain.chats.entities.chats import ChatEntity
from domain.chats.interfaces.repository import BaseChatsRepository


@dataclass
class DummyInMemoryChatsRepository(BaseChatsRepository):
    _saved_chats: list[ChatEntity] = field(default_factory=list, kw_only=True)

    async def check_chat_exists_by_title(self, title: str) -> bool:
        return any(chat.title.as_generic_type() == title for chat in self._saved_chats)

    async def get_chat_by_oid(self, oid: str) -> ChatEntity | None:
        try:
            return next(chat for chat in self._saved_chats if str(chat.oid) == oid)
        except StopIteration:
            return None

    async def add_chat(self, chat: ChatEntity) -> None:
        self._saved_chats.append(chat)

    async def delete_chat_by_oid(self, chat_oid: str) -> None:
        self._saved_chats[:] = [chat for chat in self._saved_chats if str(chat.oid) != chat_oid]
