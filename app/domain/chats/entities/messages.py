from dataclasses import dataclass
from uuid import UUID

from domain.base.entity import BaseEntity
from domain.chats.value_objects.messages import MessageContentValueObject


@dataclass(eq=False)
class MessageEntity(BaseEntity):
    chat_id: UUID
    sender_id: UUID
    content: MessageContentValueObject
