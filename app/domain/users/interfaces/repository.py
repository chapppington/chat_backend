from abc import (
    ABC,
    abstractmethod,
)
from uuid import UUID

from domain.users.entities import UserEntity


class BaseUserRepository(ABC):
    @abstractmethod
    async def add(self, user: UserEntity) -> None: ...

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> UserEntity | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> UserEntity | None: ...
