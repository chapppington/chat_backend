from fastapi import FastAPI
from fastapi.testclient import TestClient

import pytest
import pytest_asyncio
from faker import Faker
from presentation.api.auth import auth_service
from presentation.api.main import create_app
from punq import Container

from application.container import init_container
from application.mediator import Mediator
from application.users.commands import CreateUserCommand
from domain.users.entities import UserEntity
from tests.fixtures import init_dummy_container


@pytest.fixture
def container() -> Container:
    return init_dummy_container()


@pytest.fixture
def app(container: Container) -> FastAPI:
    app = create_app()
    app.dependency_overrides[init_container] = lambda: container

    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app=app)


@pytest.fixture
def mediator(container: Container) -> Mediator:
    return container.resolve(Mediator)


@pytest_asyncio.fixture
async def authenticated_user(mediator: Mediator, faker: Faker) -> UserEntity:
    email = faker.email()
    password = faker.password(length=12)
    name = faker.name()

    result, *_ = await mediator.handle_command(
        CreateUserCommand(email=email, password=password, name=name),
    )

    return result


@pytest_asyncio.fixture
async def authenticated_client(
    client: TestClient,
    authenticated_user: UserEntity,
) -> TestClient:
    user_id = str(authenticated_user.oid)
    access_token = auth_service.create_access_token(uid=user_id)
    refresh_token = auth_service.create_refresh_token(uid=user_id)

    client.cookies.set("access_token", access_token)
    client.cookies.set("refresh_token", refresh_token)

    return client
