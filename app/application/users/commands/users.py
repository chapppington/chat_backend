from dataclasses import dataclass
from io import BytesIO
from uuid import UUID

from application.base.command import (
    BaseCommand,
    BaseCommandHandler,
)
from domain.users.entities import UserEntity
from domain.users.interfaces.relationship_repository import BaseRelationshipRepository
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
    relationship_repository: BaseRelationshipRepository

    async def handle(self, command: CreateUserCommand) -> UserEntity:
        result = await self.user_service.create_user(
            email=command.email,
            password=command.password,
            name=command.name,
        )

        # Create user node in Neo4j after user is created
        name_parts = command.name.strip().split(maxsplit=1)
        first_name = name_parts[0] if name_parts else command.name
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        await self.relationship_repository.create_user_node(
            user_id=result.oid,
            first_name=first_name,
            last_name=last_name,
            city=None,  # Can be added later if needed
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
