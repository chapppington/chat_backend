from functools import lru_cache

from infrastructure.database.gateways.postgres import Database
from infrastructure.database.repositories.users.users import SQLAlchemyUserRepository
from infrastructure.neo4j.client import Neo4jClient
from infrastructure.neo4j.repositories.relationships import Neo4jRelationshipRepository
from infrastructure.s3.client import S3Client
from infrastructure.s3.storage import S3FileStorage
from punq import (
    Container,
    Scope,
)

from application.mediator import Mediator
from application.users.commands import (
    AddFriendCommand,
    AddFriendCommandHandler,
    AddRelationshipCommand,
    AddRelationshipCommandHandler,
    CreateUserCommand,
    CreateUserCommandHandler,
    FollowUserCommand,
    FollowUserCommandHandler,
    RemoveFriendCommand,
    RemoveFriendCommandHandler,
    UnfollowUserCommand,
    UnfollowUserCommandHandler,
    UploadAvatarCommand,
    UploadAvatarCommandHandler,
)
from application.users.queries import (
    AuthenticateUserQuery,
    AuthenticateUserQueryHandler,
    CheckRelationshipQuery,
    CheckRelationshipQueryHandler,
    GetFollowersQuery,
    GetFollowersQueryHandler,
    GetFollowingQuery,
    GetFollowingQueryHandler,
    GetFriendsQuery,
    GetFriendsQueryHandler,
    GetMutualFriendsQuery,
    GetMutualFriendsQueryHandler,
    GetUserByIdQuery,
    GetUserByIdQueryHandler,
)
from domain.base.file_storage import BaseFileStorage
from domain.users.interfaces.relationship_repository import BaseRelationshipRepository
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

    # Регистрируем Neo4jClient
    def init_neo4j_client() -> Neo4jClient:
        return Neo4jClient(config=config)

    container.register(Neo4jClient, factory=init_neo4j_client, scope=Scope.singleton)

    # Регистрируем репозитории
    container.register(
        BaseUserRepository,
        SQLAlchemyUserRepository,
    )

    # Регистрируем Relationship Repository
    def init_relationship_repository() -> BaseRelationshipRepository:
        neo4j_client = container.resolve(Neo4jClient)
        return Neo4jRelationshipRepository(neo4j_client=neo4j_client)

    container.register(
        BaseRelationshipRepository,
        factory=init_relationship_repository,
        scope=Scope.singleton,
    )

    # Регистрируем доменные сервисы
    container.register(UserService)

    # Регистрируем command handlers
    # Users
    container.register(CreateUserCommandHandler)
    container.register(UploadAvatarCommandHandler)
    # Relationships
    container.register(AddFriendCommandHandler)
    container.register(RemoveFriendCommandHandler)
    container.register(FollowUserCommandHandler)
    container.register(UnfollowUserCommandHandler)
    container.register(AddRelationshipCommandHandler)

    # Регистрируем query handlers
    # Users
    container.register(AuthenticateUserQueryHandler)
    container.register(GetUserByIdQueryHandler)
    # Relationships
    container.register(GetFriendsQueryHandler)
    container.register(GetFollowersQueryHandler)
    container.register(GetFollowingQueryHandler)
    container.register(GetMutualFriendsQueryHandler)
    container.register(CheckRelationshipQueryHandler)

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
        # Relationships
        mediator.register_command(
            AddFriendCommand,
            [container.resolve(AddFriendCommandHandler)],
        )
        mediator.register_command(
            RemoveFriendCommand,
            [container.resolve(RemoveFriendCommandHandler)],
        )
        mediator.register_command(
            FollowUserCommand,
            [container.resolve(FollowUserCommandHandler)],
        )
        mediator.register_command(
            UnfollowUserCommand,
            [container.resolve(UnfollowUserCommandHandler)],
        )
        mediator.register_command(
            AddRelationshipCommand,
            [container.resolve(AddRelationshipCommandHandler)],
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
        # Relationships
        mediator.register_query(
            GetFriendsQuery,
            container.resolve(GetFriendsQueryHandler),
        )
        mediator.register_query(
            GetFollowersQuery,
            container.resolve(GetFollowersQueryHandler),
        )
        mediator.register_query(
            GetFollowingQuery,
            container.resolve(GetFollowingQueryHandler),
        )
        mediator.register_query(
            GetMutualFriendsQuery,
            container.resolve(GetMutualFriendsQueryHandler),
        )
        mediator.register_query(
            CheckRelationshipQuery,
            container.resolve(CheckRelationshipQueryHandler),
        )

        return mediator

    container.register(Mediator, factory=init_mediator, scope=Scope.singleton)

    return container
