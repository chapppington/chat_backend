from dataclasses import (
    dataclass,
    field,
)
from typing import Iterable
from uuid import UUID

from domain.chats.entities.messages import MessageEntity
from domain.chats.filters.messages import GetMessagesFilters
from domain.chats.interfaces.repository import BaseMessagesRepository


@dataclass
class DummyInMemoryMessagesRepository(BaseMessagesRepository):
    _saved_messages: list[MessageEntity] = field(default_factory=list, kw_only=True)

    async def add_message(self, message: MessageEntity) -> None:
        self._saved_messages.append(message)

    async def get_messages(
        self,
        chat_id: UUID,
        filters: GetMessagesFilters,
    ) -> tuple[Iterable[MessageEntity], int]:
        filtered_messages = [message for message in self._saved_messages if message.chat_id == chat_id]

        total = len(filtered_messages)

        sorted_messages = sorted(
            filtered_messages,
            key=lambda m: m.created_at,
            reverse=True,
        )

        paginated_messages = sorted_messages[filters.offset : filters.offset + filters.limit]

        return paginated_messages, total
