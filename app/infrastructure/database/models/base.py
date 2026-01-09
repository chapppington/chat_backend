import datetime
from uuid import UUID

from sqlalchemy import sql
from sqlalchemy.dialects.postgresql import UUID as UUIDType
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)


class BaseModel(DeclarativeBase):
    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        """Relationships не используются в repr(), т.к.

        могут вести к неожиданным подгрузкам

        """
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"


class TimedBaseModel(BaseModel):
    __abstract__ = True

    oid: Mapped[UUID] = mapped_column(UUIDType[UUID](as_uuid=True), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        nullable=False,
        server_default=sql.func.now(),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        nullable=False,
        server_default=sql.func.now(),
        onupdate=sql.func.now(),
    )
