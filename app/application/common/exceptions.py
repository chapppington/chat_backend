from dataclasses import dataclass

from application.base.exception import LogicException


@dataclass(eq=False)
class CommandHandlersNotRegisteredException(LogicException):
    command_type: type

    @property
    def message(self) -> str:
        return f"Command handlers not registered for command type: {self.command_type.__name__}"


@dataclass(eq=False)
class QueryHandlerNotRegisteredException(LogicException):
    query_type: type

    @property
    def message(self) -> str:
        return f"Query handler not registered for query type: {self.query_type.__name__}"
