from functools import lru_cache

from infrastructure.database.gateways.postgres import Database
from infrastructure.database.repositories.users.users import SQLAlchemyUserRepository
from punq import (
    Container,
    Scope,
)

from application.mediator import Mediator
from application.users.commands import (
    CreateUserCommand,
    CreateUserCommandHandler,
)
from application.users.queries import (
    AuthenticateUserQuery,
    AuthenticateUserQueryHandler,
    GetUserByIdQuery,
    GetUserByIdQueryHandler,
)
from domain.users.interfaces.repository import BaseUserRepository
from domain.users.services import UserService
from settings.config import Config


@lru_cache(1)
def init_container():
    return _init_container()


def _init_container() -> Container:
    container = Container()

    # Регистрируем конфиг
    config = Config()
    container.register(Config, instance=config, scope=Scope.singleton)

    # Регистрируем Database
    def init_database() -> Database:
        return Database(
            url=config.postgres_connection_uri,
            ro_url=config.postgres_connection_uri,
        )

    container.register(Database, factory=init_database, scope=Scope.singleton)

    # Регистрируем репозитории
    container.register(
        BaseUserRepository,
        SQLAlchemyUserRepository,
    )

    # Регистрируем доменные сервисы
    container.register(UserService)

    # Регистрируем command handlers
    # Users
    container.register(CreateUserCommandHandler)

    # Регистрируем query handlers
    # Users
    container.register(AuthenticateUserQueryHandler)
    container.register(GetUserByIdQueryHandler)

    # Инициализируем медиатор
    def init_mediator() -> Mediator:
        mediator = Mediator()

        # Регистрируем commands
        # Users
        mediator.register_command(
            CreateUserCommand,
            [container.resolve(CreateUserCommandHandler)],
        )

        # Регистрируем queries
        # Users
        mediator.register_query(
            AuthenticateUserQuery,
            container.resolve(AuthenticateUserQueryHandler),
        )
        mediator.register_query(
            GetUserByIdQuery,
            container.resolve(GetUserByIdQueryHandler),
        )

        return mediator

    container.register(Mediator, factory=init_mediator, scope=Scope.singleton)

    return container
