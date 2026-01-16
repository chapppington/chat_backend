from dataclasses import dataclass
from uuid import UUID

from application.base.command import (
    BaseCommand,
    BaseCommandHandler,
)
from domain.chats.entities.chats import ChatEntity
from domain.chats.exceptions.chats import (
    ChatAlreadyExistsException,
    ChatNotFoundException,
)
from domain.chats.interfaces.repository import BaseChatsRepository
from domain.chats.value_objects.chats import ChatTitleValueObject


@dataclass(frozen=True)
class CreateChatCommand(BaseCommand):
    title: str
    owner_id: UUID


@dataclass(frozen=True)
class CreateChatCommandHandler(
    BaseCommandHandler[CreateChatCommand, ChatEntity],
):
    chats_repository: BaseChatsRepository

    async def handle(self, command: CreateChatCommand) -> ChatEntity:
        title_vo = ChatTitleValueObject(value=command.title)

        exists = await self.chats_repository.check_chat_exists_by_title(title_vo.as_generic_type())
        if exists:
            raise ChatAlreadyExistsException(title=title_vo.as_generic_type())

        chat = ChatEntity(
            title=title_vo,
            owner_id=command.owner_id,
        )

        await self.chats_repository.add_chat(chat)
        return chat


@dataclass(frozen=True)
class DeleteChatCommand(BaseCommand):
    chat_id: UUID


@dataclass(frozen=True)
class DeleteChatCommandHandler(
    BaseCommandHandler[DeleteChatCommand, None],
):
    chats_repository: BaseChatsRepository

    async def handle(self, command: DeleteChatCommand) -> None:
        chat = await self.chats_repository.get_chat_by_oid(str(command.chat_id))
        if not chat:
            raise ChatNotFoundException(chat_id=command.chat_id)

        await self.chats_repository.delete_chat_by_oid(str(command.chat_id))
