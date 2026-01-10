from dataclasses import dataclass
from io import BytesIO
from uuid import UUID

from application.base.command import (
    BaseCommand,
    BaseCommandHandler,
)
from domain.users.entities import UserEntity
from domain.users.services import UserService


@dataclass(frozen=True)
class CreateUserCommand(BaseCommand):
    email: str
    password: str
    name: str


@dataclass(frozen=True)
class CreateUserCommandHandler(
    BaseCommandHandler[CreateUserCommand, UserEntity],
):
    user_service: UserService

    async def handle(self, command: CreateUserCommand) -> UserEntity:
        result = await self.user_service.create_user(
            email=command.email,
            password=command.password,
            name=command.name,
        )
        return result


@dataclass(frozen=True)
class UploadAvatarCommand(BaseCommand):
    user_id: UUID
    file_obj: BytesIO
    filename: str


@dataclass(frozen=True)
class UploadAvatarCommandHandler(
    BaseCommandHandler[UploadAvatarCommand, UserEntity],
):
    user_service: UserService

    async def handle(self, command: UploadAvatarCommand) -> UserEntity:
        result = await self.user_service.upload_avatar(
            user_id=command.user_id,
            file_obj=command.file_obj,
            filename=command.filename,
        )
        return result
