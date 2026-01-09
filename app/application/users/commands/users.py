from dataclasses import dataclass

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
