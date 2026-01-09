from fastapi import (
    FastAPI,
    status,
)
from fastapi.testclient import TestClient

import pytest
from faker import Faker
from httpx import Response

from application.mediator import Mediator
from application.users.commands import CreateUserCommand


@pytest.mark.asyncio
async def test_register_success(app: FastAPI, client: TestClient, faker: Faker):
    url = app.url_path_for("register")
    email = faker.email()
    password = faker.password(length=12)
    name = faker.name()

    response: Response = client.post(
        url=url,
        json={
            "email": email,
            "password": password,
            "name": name,
        },
    )

    assert response.is_success

    json_response = response.json()

    assert "data" in json_response
    assert json_response["data"]["email"] == email
    assert json_response["data"]["name"] == name
    assert "oid" in json_response["data"]


@pytest.mark.asyncio
async def test_register_duplicate_email(
    app: FastAPI,
    client: TestClient,
    mediator: Mediator,
    faker: Faker,
):
    url = app.url_path_for("register")
    email = faker.email()
    password = faker.password(length=12)
    name = faker.name()

    await mediator.handle_command(
        CreateUserCommand(email=email, password=password, name=name),
    )

    response: Response = client.post(
        url=url,
        json={
            "email": email,
            "password": password,
            "name": name,
        },
    )

    assert response.status_code == status.HTTP_409_CONFLICT, response.json()
    json_response = response.json()
    assert "errors" in json_response
    assert len(json_response["errors"]) > 0


@pytest.mark.asyncio
async def test_register_invalid_email(app: FastAPI, client: TestClient, faker: Faker):
    url = app.url_path_for("register")
    password = faker.password(length=12)
    name = faker.name()

    response: Response = client.post(
        url=url,
        json={
            "email": "invalid-email",
            "password": password,
            "name": name,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    json_response = response.json()
    assert "errors" in json_response
    assert len(json_response["errors"]) > 0


@pytest.mark.asyncio
async def test_register_empty_password(app: FastAPI, client: TestClient, faker: Faker):
    url = app.url_path_for("register")
    email = faker.email()
    name = faker.name()

    response: Response = client.post(
        url=url,
        json={
            "email": email,
            "password": "",
            "name": name,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    json_response = response.json()
    assert "errors" in json_response
    assert len(json_response["errors"]) > 0


@pytest.mark.asyncio
async def test_register_short_password(app: FastAPI, client: TestClient, faker: Faker):
    url = app.url_path_for("register")
    email = faker.email()
    name = faker.name()

    response: Response = client.post(
        url=url,
        json={
            "email": email,
            "password": "short",
            "name": name,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    json_response = response.json()
    assert "errors" in json_response
    assert len(json_response["errors"]) > 0


@pytest.mark.asyncio
async def test_login_success(
    app: FastAPI,
    client: TestClient,
    mediator: Mediator,
    faker: Faker,
):
    url = app.url_path_for("login")
    email = faker.email()
    password = faker.password(length=12)
    name = faker.name()

    await mediator.handle_command(
        CreateUserCommand(email=email, password=password, name=name),
    )

    response: Response = client.post(
        url=url,
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.is_success

    json_response = response.json()

    assert "data" in json_response
    assert "access_token" in json_response["data"]
    assert "refresh_token" in json_response["data"]
    assert len(json_response["data"]["access_token"]) > 0
    assert len(json_response["data"]["refresh_token"]) > 0

    cookies = response.cookies
    assert "access_token" in cookies
    assert "refresh_token" in cookies


@pytest.mark.asyncio
async def test_login_invalid_email(app: FastAPI, client: TestClient):
    url = app.url_path_for("login")

    response: Response = client.post(
        url=url,
        json={
            "email": "nonexistent@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.json()
    json_response = response.json()
    assert "errors" in json_response
    assert len(json_response["errors"]) > 0


@pytest.mark.asyncio
async def test_login_invalid_password(
    app: FastAPI,
    client: TestClient,
    mediator: Mediator,
    faker: Faker,
):
    url = app.url_path_for("login")
    email = faker.email()
    password = faker.password(length=12)
    name = faker.name()

    await mediator.handle_command(
        CreateUserCommand(email=email, password=password, name=name),
    )

    response: Response = client.post(
        url=url,
        json={
            "email": email,
            "password": "wrong_password",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.json()
    json_response = response.json()
    assert "errors" in json_response
    assert len(json_response["errors"]) > 0


@pytest.mark.asyncio
async def test_refresh_token_success(
    app: FastAPI,
    client: TestClient,
    mediator: Mediator,
    faker: Faker,
):
    login_url = app.url_path_for("login")
    refresh_url = app.url_path_for("refresh_token")
    email = faker.email()
    password = faker.password(length=12)
    name = faker.name()

    await mediator.handle_command(
        CreateUserCommand(email=email, password=password, name=name),
    )

    login_response: Response = client.post(
        url=login_url,
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.is_success

    refresh_response: Response = client.post(url=refresh_url)

    assert refresh_response.is_success

    json_response = refresh_response.json()

    assert "data" in json_response
    assert "access_token" in json_response["data"]
    assert len(json_response["data"]["access_token"]) > 0

    cookies = refresh_response.cookies
    assert "access_token" in cookies


@pytest.mark.asyncio
async def test_refresh_token_without_cookie(app: FastAPI, client: TestClient):
    url = app.url_path_for("refresh_token")

    response: Response = client.post(url=url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.json()
    json_response = response.json()
    assert "errors" in json_response
    assert len(json_response["errors"]) > 0
