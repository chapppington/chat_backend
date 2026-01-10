from functools import lru_cache

from infrastructure.database.gateways.postgres import Database
from infrastructure.database.repositories.users.users import SQLAlchemyUserRepository
from infrastructure.s3.client import S3Client
from infrastructure.s3.storage import S3FileStorage
from punq import (
    Container,
    Scope,
)

from application.mediator import Mediator
from application.users.commands import (
    CreateUserCommand,
    CreateUserCommandHandler,
    UploadAvatarCommand,
    UploadAvatarCommandHandler,
)
from application.users.queries import (
    AuthenticateUserQuery,
    AuthenticateUserQueryHandler,
    GetUserByIdQuery,
    GetUserByIdQueryHandler,
)
from domain.base.file_storage import BaseFileStorage
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

    # Регистрируем S3Client
    def init_s3_client() -> S3Client:
        return S3Client(config=config)

    container.register(S3Client, factory=init_s3_client, scope=Scope.singleton)

    # Регистрируем FileStorage
    def init_file_storage() -> BaseFileStorage:
        s3_client = container.resolve(S3Client)
        return S3FileStorage(s3_client=s3_client)

    container.register(BaseFileStorage, factory=init_file_storage, scope=Scope.singleton)

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
    container.register(UploadAvatarCommandHandler)

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
        mediator.register_command(
            UploadAvatarCommand,
            [container.resolve(UploadAvatarCommandHandler)],
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
