from dataclasses import (
    dataclass,
    field,
)
from uuid import UUID

from domain.users.entities import UserEntity
from domain.users.interfaces.repository import BaseUserRepository


@dataclass
class DummyInMemoryUserRepository(BaseUserRepository):
    _saved_users: list[UserEntity] = field(default_factory=list, kw_only=True)

    async def add(self, user: UserEntity) -> None:
        self._saved_users.append(user)

    async def get_by_id(self, user_id: UUID) -> UserEntity | None:
        try:
            return next(user for user in self._saved_users if user.oid == user_id)
        except StopIteration:
            return None

    async def get_by_email(self, email: str) -> UserEntity | None:
        search_term = email.lower()
        try:
            return next(user for user in self._saved_users if user.email.as_generic_type().lower() == search_term)
        except StopIteration:
            return None
