from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import (
    Any,
    Generic,
    TypeVar,
)


@dataclass(frozen=True)
class BaseQuery(ABC): ...


QueryType = TypeVar("QueryType", bound=BaseQuery)
QueryResultType = TypeVar("QueryResultType", bound=Any)


@dataclass(frozen=True)
class BaseQueryHandler(ABC, Generic[QueryType, QueryResultType]):
    @abstractmethod
    async def handle(self, query: QueryType) -> QueryResultType: ...
