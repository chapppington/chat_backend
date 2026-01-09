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
class BaseCommand(ABC): ...


CommandType = TypeVar("CommandType", bound=BaseCommand)
CommandResultType = TypeVar("CommandResultType", bound=Any)


@dataclass(frozen=True)
class BaseCommandHandler(ABC, Generic[CommandType, CommandResultType]):
    @abstractmethod
    async def handle(self, command: CommandType) -> CommandResultType: ...
