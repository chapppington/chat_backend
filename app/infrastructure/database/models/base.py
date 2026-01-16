import datetime
from uuid import UUID

from sqlalchemy import (
    MetaData,
    sql,
)
from sqlalchemy.dialects.postgresql import UUID as UUIDType
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)


metadata = MetaData(
    naming_convention={
        "pk": "pk_%(table_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "ix": "ix_%(table_name)s_%(column_0_name)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
    },
)


class BaseModel(DeclarativeBase):
    metadata = metadata
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
