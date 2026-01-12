from dataclasses import dataclass
from uuid import (
    UUID,
    uuid4,
)

from infrastructure.database.converters.users.user import (
    user_entity_to_model,
    user_model_to_entity,
)
from infrastructure.database.gateways.postgres import Database
from infrastructure.database.models.outbox.outbox import (
    OutboxEventModel,
    OutboxEventStatus,
)
from infrastructure.database.models.users.user import UserModel
from sqlalchemy import (
    func,
    select,
)

from domain.users.entities import UserEntity
from domain.users.interfaces.repository import BaseUserRepository


@dataclass
class SQLAlchemyUserRepository(BaseUserRepository):
    database: Database

    async def add(self, user: UserEntity) -> None:
        async with self.database.get_session() as session:
            user_model = user_entity_to_model(user)
            session.add(user_model)

            # Создаем событие в outbox в рамках той же транзакции
            outbox_event = OutboxEventModel(
                oid=uuid4(),
                event_type="user.created",
                aggregate_type="user",
                aggregate_id=str(user.oid),
                payload={
                    "user_id": str(user.oid),
                    "email": user.email.as_generic_type(),
                    "name": user.name.as_generic_type(),
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                },
                status=OutboxEventStatus.PENDING.value,
            )
            session.add(outbox_event)

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
