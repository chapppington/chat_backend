from dataclasses import dataclass
from uuid import UUID

from application.base.query import (
    BaseQuery,
    BaseQueryHandler,
)
from domain.users.entities import UserEntity
from domain.users.services import UserService


@dataclass(frozen=True)
class AuthenticateUserQuery(BaseQuery):
    email: str
    password: str


@dataclass(frozen=True)
class GetUserByIdQuery(BaseQuery):
    user_id: UUID


@dataclass(frozen=True)
class AuthenticateUserQueryHandler(
    BaseQueryHandler[AuthenticateUserQuery, UserEntity],
):
    user_service: UserService

    async def handle(
        self,
        query: AuthenticateUserQuery,
    ) -> UserEntity:
        return await self.user_service.authenticate_user(
            email=query.email,
            password=query.password,
        )


@dataclass(frozen=True)
class GetUserByIdQueryHandler(
    BaseQueryHandler[GetUserByIdQuery, UserEntity],
):
    user_service: UserService

    async def handle(
        self,
        query: GetUserByIdQuery,
    ) -> UserEntity:
        return await self.user_service.get_by_id(
            user_id=query.user_id,
        )
