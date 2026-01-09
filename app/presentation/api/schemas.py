from typing import (
    Any,
    Generic,
    TypeVar,
)

from presentation.api.filters import PaginationOut
from pydantic import (
    BaseModel,
    Field,
)


TData = TypeVar("TData")
TListItem = TypeVar("TListItem")


class PingResponseSchema(BaseModel):
    result: bool


class ListPaginatedResponse(BaseModel, Generic[TListItem]):
    items: list[TListItem]
    pagination: PaginationOut


class ApiResponse(BaseModel, Generic[TData]):
    data: TData | dict = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    errors: list[Any] = Field(default_factory=list)


class ErrorDetailSchema(BaseModel):
    message: str
    type: str | None = None


class ErrorResponseSchema(BaseModel):
    data: dict = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    errors: list[ErrorDetailSchema] = Field(default_factory=list)
