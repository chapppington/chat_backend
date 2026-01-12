from enum import Enum
from typing import (
    Any,
    Dict,
    Optional,
)

from infrastructure.database.models.base import TimedBaseModel
from sqlalchemy import (
    JSON,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)


class OutboxEventStatus(str, Enum):
    PENDING = "pending"
    PROCESSED = "processed"


class OutboxEventModel(TimedBaseModel):
    __tablename__ = "outbox_events"

    event_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Тип события (например, user.created)",
    )
    aggregate_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Тип агрегата (например, user)",
    )
    aggregate_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="ID агрегата",
    )
    payload: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        comment="Данные события в формате JSON",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=OutboxEventStatus.PENDING.value,
        comment="Статус обработки события",
    )
    processed_at: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Время обработки события",
    )
