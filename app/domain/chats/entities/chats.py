from dataclasses import (
    dataclass,
    field,
)
from uuid import UUID

from domain.base.entity import BaseEntity
from domain.chats.entities.messages import MessageEntity
from domain.chats.value_objects.chats import ChatTitleValueObject


@dataclass(eq=False)
class ChatEntity(BaseEntity):
    owner_id: UUID
    title: ChatTitleValueObject
    messages: set[MessageEntity] = field(
        default_factory=set,
        kw_only=True,
    )

    def add_message(self, message: MessageEntity) -> None:
        self.messages.add(message)
