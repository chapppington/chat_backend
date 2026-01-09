from datetime import datetime
from typing import Optional

from infrastructure.database.models.base import TimedBaseModel
from sqlalchemy import (
    DateTime,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)


class UserModel(TimedBaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_online_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
