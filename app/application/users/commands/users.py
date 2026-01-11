from dataclasses import dataclass
from io import BytesIO
from uuid import UUID

from application.base.command import (
    BaseCommand,
    BaseCommandHandler,
)
from domain.users.entities import UserEntity
from domain.users.interfaces.relationship_repository import BaseRelationshipRepository
from domain.users.interfaces.repository import BaseUserRepository
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
    user_repository: BaseUserRepository
    relationship_repository: BaseRelationshipRepository

    async def handle(self, command: CreateUserCommand) -> UserEntity:
        # Step 1: Create user in PostgreSQL
        result = await self.user_service.create_user(
            email=command.email,
            password=command.password,
            name=command.name,
        )

        # Step 2: Create user node in Neo4j
        # If this fails, we need to rollback PostgreSQL (compensating transaction)
        name_parts = command.name.strip().split(maxsplit=1)
        first_name = name_parts[0] if name_parts else command.name
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        try:
            await self.relationship_repository.create_user_node(
                user_id=result.oid,
                first_name=first_name,
                last_name=last_name,
                city=None,  # Can be added later if needed
            )
        except Exception as e:
            # Compensating transaction: rollback PostgreSQL if Neo4j fails
            try:
                await self.user_repository.delete(result.oid)
            except Exception:
                # Log rollback error but re-raise original exception
                # In production, you might want to use proper logging here
                pass
            raise e

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
