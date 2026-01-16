from dataclasses import dataclass
from uuid import UUID

from infrastructure.database.converters.users.user import (
    user_entity_to_model,
    user_model_to_entity,
)
from infrastructure.database.gateways.postgres import SQLDatabase
from infrastructure.database.models.users.user import UserModel
from sqlalchemy import (
    func,
    select,
    update,
)

from domain.users.entities import UserEntity
from domain.users.interfaces.repository import BaseUserRepository


@dataclass
class SQLAlchemyUserRepository(BaseUserRepository):
    database: SQLDatabase

    async def add(self, user: UserEntity) -> None:
        async with self.database.get_session() as session:
            user_model = user_entity_to_model(user)
            session.add(user_model)
            await session.commit()

    async def get_by_id(self, user_id: UUID) -> UserEntity | None:
        async with self.database.get_read_only_session() as session:
            stmt = select(UserModel).where(UserModel.oid == user_id)
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()
            return user_model_to_entity(result) if result else None

    async def get_by_email(self, email: str) -> UserEntity | None:
        async with self.database.get_read_only_session() as session:
            stmt = select(UserModel).where(func.lower(UserModel.email) == email.lower())
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()
            return user_model_to_entity(result) if result else None

    async def update_avatar_path(self, user_id: UUID, avatar_path: str | None) -> None:
        async with self.database.get_session() as session:
            stmt = update(UserModel).where(UserModel.oid == user_id).values(avatar_path=avatar_path)
            await session.execute(stmt)
            await session.commit()
