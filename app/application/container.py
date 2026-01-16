from functools import lru_cache

from infrastructure.database.gateways.postgres import SQLDatabase
from infrastructure.database.repositories.chats.chats import MongoDBChatsRepository
from infrastructure.database.repositories.chats.messages import MongoDBMessagesRepository
from infrastructure.database.repositories.users.users import SQLAlchemyUserRepository
from infrastructure.s3.client import S3Client
from infrastructure.s3.storage import S3FileStorage
from infrastructure.websockets.manager import (
    BaseConnectionManager,
    ConnectionManager,
)
from motor.motor_asyncio import AsyncIOMotorClient
from punq import (
    Container,
    Scope,
)

from application.chats.commands import (
    CreateChatCommand,
    CreateChatCommandHandler,
    CreateMessageCommand,
    CreateMessageCommandHandler,
    DeleteChatCommand,
    DeleteChatCommandHandler,
)
from application.chats.queries import (
    GetChatByIdQuery,
    GetChatByIdQueryHandler,
    GetMessagesQuery,
    GetMessagesQueryHandler,
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
from domain.chats.interfaces import BaseChatsRepository
from domain.chats.interfaces.repository import BaseMessagesRepository
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

    # WebSocket Manager
    container.register(
        BaseConnectionManager,
        instance=ConnectionManager(),
        scope=Scope.singleton,
    )

    # Регистрируем SQL Database
    def init_sql_database() -> SQLDatabase:
        return SQLDatabase(
            url=config.postgres_connection_uri,
            ro_url=config.postgres_connection_uri,
        )

    container.register(SQLDatabase, factory=init_sql_database, scope=Scope.singleton)

    # Регистрируем S3Client
    def init_s3_client() -> S3Client:
        return S3Client(config=config)

    container.register(S3Client, factory=init_s3_client, scope=Scope.singleton)

    # Регистрируем FileStorage
    def init_file_storage() -> BaseFileStorage:
        s3_client = container.resolve(S3Client)
        return S3FileStorage(s3_client=s3_client)

    container.register(BaseFileStorage, factory=init_file_storage, scope=Scope.singleton)

    # Регистрируем MongoDB Client
    def create_mongodb_client():
        return AsyncIOMotorClient(
            config.mongodb_connection_uri,
            serverSelectionTimeoutMS=3000,
        )

    container.register(
        AsyncIOMotorClient,
        factory=create_mongodb_client,
        scope=Scope.singleton,
    )

    mongodb_client = container.resolve(AsyncIOMotorClient)

    # Регистрируем репозитории
    def init_chats_mongodb_repository() -> BaseChatsRepository:
        return MongoDBChatsRepository(
            mongo_db_client=mongodb_client,
            mongo_db_database_name=config.mongo_database,
            mongo_db_collection_name=config.mongodb_chat_collection,
        )

    def init_messages_mongodb_repository() -> BaseMessagesRepository:
        return MongoDBMessagesRepository(
            mongo_db_client=mongodb_client,
            mongo_db_database_name=config.mongo_database,
            mongo_db_collection_name=config.mongodb_message_collection,
        )

    container.register(BaseChatsRepository, factory=init_chats_mongodb_repository)
    container.register(
        BaseMessagesRepository,
        factory=init_messages_mongodb_repository,
    )

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

    # Chats
    container.register(CreateChatCommandHandler)
    container.register(DeleteChatCommandHandler)
    container.register(CreateMessageCommandHandler)

    # Регистрируем query handlers
    # Users
    container.register(AuthenticateUserQueryHandler)
    container.register(GetUserByIdQueryHandler)

    # Chats
    container.register(GetChatByIdQueryHandler)
    container.register(GetMessagesQueryHandler)

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

        # Chats
        mediator.register_command(
            CreateChatCommand,
            [container.resolve(CreateChatCommandHandler)],
        )
        mediator.register_command(
            DeleteChatCommand,
            [container.resolve(DeleteChatCommandHandler)],
        )
        mediator.register_command(
            CreateMessageCommand,
            [container.resolve(CreateMessageCommandHandler)],
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

        # Chats
        mediator.register_query(
            GetChatByIdQuery,
            container.resolve(GetChatByIdQueryHandler),
        )
        mediator.register_query(
            GetMessagesQuery,
            container.resolve(GetMessagesQueryHandler),
        )

        return mediator

    container.register(Mediator, factory=init_mediator, scope=Scope.singleton)

    return container
