from dataclasses import dataclass
from uuid import UUID

from application.base.command import (
    BaseCommand,
    BaseCommandHandler,
)
from domain.chats.entities.messages import MessageEntity
from domain.chats.interfaces.repository import BaseMessagesRepository
from domain.chats.value_objects.messages import MessageContentValueObject


@dataclass(frozen=True)
class CreateMessageCommand(BaseCommand):
    chat_id: UUID
    sender_id: UUID
    content: str


@dataclass(frozen=True)
class CreateMessageCommandHandler(
    BaseCommandHandler[CreateMessageCommand, MessageEntity],
):
    messages_repository: BaseMessagesRepository

    async def handle(self, command: CreateMessageCommand) -> MessageEntity:
        content_vo = MessageContentValueObject(value=command.content)

        message = MessageEntity(
            chat_id=command.chat_id,
            sender_id=command.sender_id,
            content=content_vo,
        )

        await self.messages_repository.add_message(message)
        return message
