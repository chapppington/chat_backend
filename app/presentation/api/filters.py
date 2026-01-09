from pydantic import (
    BaseModel,
    Field,
)


class PaginationOut(BaseModel):
    limit: int
    offset: int
    total: int


class PaginationIn(BaseModel):
    limit: int = Field(default=10)
    offset: int = Field(default=0)
