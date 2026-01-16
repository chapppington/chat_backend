from typing import (
    Any,
    Mapping,
)
from uuid import UUID

from domain.chats.entities.chats import ChatEntity
from domain.chats.entities.messages import MessageEntity
from domain.chats.value_objects.chats import ChatTitleValueObject
from domain.chats.value_objects.messages import MessageContentValueObject


def chat_entity_to_document(chat: ChatEntity) -> dict[str, Any]:
    return {
        "oid": str(chat.oid),
        "title": chat.title.as_generic_type(),
        "owner_id": str(chat.owner_id),
        "created_at": chat.created_at,
        "updated_at": chat.updated_at,
    }


def chat_document_to_entity(chat_document: Mapping[str, Any]) -> ChatEntity:
    return ChatEntity(
        oid=UUID(chat_document["oid"]),
        title=ChatTitleValueObject(value=chat_document["title"]),
        owner_id=UUID(chat_document["owner_id"]),
        created_at=chat_document["created_at"],
        updated_at=chat_document["updated_at"],
    )


def message_entity_to_document(message: MessageEntity) -> dict[str, Any]:
    return {
        "oid": str(message.oid),
        "chat_id": str(message.chat_id),
        "sender_id": str(message.sender_id),
        "content": message.content.as_generic_type(),
        "created_at": message.created_at,
        "updated_at": message.updated_at,
    }


def message_document_to_entity(message_document: Mapping[str, Any]) -> MessageEntity:
    return MessageEntity(
        oid=UUID(message_document["oid"]),
        chat_id=UUID(message_document["chat_id"]),
        sender_id=UUID(message_document["sender_id"]),
        content=MessageContentValueObject(value=message_document["content"]),
        created_at=message_document["created_at"],
        updated_at=message_document["updated_at"],
    )
