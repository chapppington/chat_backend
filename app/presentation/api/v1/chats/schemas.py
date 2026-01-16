from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from domain.chats.entities.chats import ChatEntity
from domain.chats.entities.messages import MessageEntity


class ChatResponseSchema(BaseModel):
    oid: UUID
    title: str
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: ChatEntity) -> "ChatResponseSchema":
        return cls(
            oid=entity.oid,
            title=entity.title.as_generic_type(),
            owner_id=entity.owner_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class CreateChatRequestSchema(BaseModel):
    title: str


class MessageResponseSchema(BaseModel):
    oid: UUID
    chat_id: UUID
    sender_id: UUID
    content: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: MessageEntity) -> "MessageResponseSchema":
        return cls(
            oid=entity.oid,
            chat_id=entity.chat_id,
            sender_id=entity.sender_id,
            content=entity.content.as_generic_type(),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class CreateMessageRequestSchema(BaseModel):
    content: str


class MessagesListResponseSchema(BaseModel):
    items: list[MessageResponseSchema]
    total: int
