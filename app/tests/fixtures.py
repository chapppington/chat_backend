from infrastructure.database.repositories.dummy.users.users import DummyInMemoryUserRepository
from punq import (
    Container,
    Scope,
)

from application.container import _init_container
from domain.users.interfaces.repository import BaseUserRepository


def init_dummy_container() -> Container:
    container = _init_container()

    # Регистрируем репозитории (dummy для начала)
    container.register(
        BaseUserRepository,
        DummyInMemoryUserRepository,
        scope=Scope.singleton,
    )
    return container
