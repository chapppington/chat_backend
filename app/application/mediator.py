from collections import defaultdict
from collections.abc import Iterable
from dataclasses import (
    dataclass,
    field,
)

from application.base.command import (
    BaseCommand,
    BaseCommandHandler,
    CommandResultType,
    CommandType,
)
from application.base.query import (
    BaseQuery,
    BaseQueryHandler,
    QueryResultType,
    QueryType,
)
from application.common.exceptions import (
    CommandHandlersNotRegisteredException,
    QueryHandlerNotRegisteredException,
)


@dataclass(eq=False)
class Mediator:
    commands_map: dict[CommandType, BaseCommandHandler] = field(
        default_factory=lambda: defaultdict(list),
        kw_only=True,
    )

    queries_map: dict[QueryType, BaseQueryHandler] = field(
        default_factory=dict,
        kw_only=True,
    )

    def register_command(
        self,
        command: CommandType,
        command_handlers: Iterable[BaseCommandHandler[CommandType, CommandResultType]],
    ):
        self.commands_map[command].extend(command_handlers)

    def register_query(
        self,
        query: QueryType,
        query_handler: BaseQueryHandler[QueryType, QueryResultType],
    ):
        self.queries_map[query] = query_handler

    async def handle_command(self, command: BaseCommand) -> Iterable[CommandResultType]:
        command_type = command.__class__

        handlers = self.commands_map.get(command_type)

        if not handlers:
            raise CommandHandlersNotRegisteredException(command_type)

        return [await handler.handle(command) for handler in handlers]

    async def handle_query(self, query: BaseQuery) -> QueryResultType:
        query_type = query.__class__
        handler = self.queries_map.get(query_type)

        if not handler:
            raise QueryHandlerNotRegisteredException(query_type)

        return await handler.handle(query=query)
