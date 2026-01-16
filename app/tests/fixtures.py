from infrastructure.database.repositories.dummy.chats.chats import DummyInMemoryChatsRepository
from infrastructure.database.repositories.dummy.chats.messages import DummyInMemoryMessagesRepository
from infrastructure.database.repositories.dummy.users.users import DummyInMemoryUserRepository
from infrastructure.s3.dummy import DummyFileStorage
from punq import (
    Container,
    Scope,
)

from application.container import _init_container
from domain.base.file_storage import BaseFileStorage
from domain.chats.interfaces.repository import (
    BaseChatsRepository,
    BaseMessagesRepository,
)
from domain.users.interfaces.repository import BaseUserRepository


def init_dummy_container() -> Container:
    container = _init_container()

    # Регистрируем dummy репозитории как синглтоны
    container.register(
        BaseUserRepository,
        DummyInMemoryUserRepository,
        scope=Scope.singleton,
    )

    container.register(
        BaseChatsRepository,
        DummyInMemoryChatsRepository,
        scope=Scope.singleton,
    )

    container.register(
        BaseMessagesRepository,
        DummyInMemoryMessagesRepository,
        scope=Scope.singleton,
    )

    # Регистрируем dummy file storage
    container.register(
        BaseFileStorage,
        DummyFileStorage,
        scope=Scope.singleton,
    )

    return container
