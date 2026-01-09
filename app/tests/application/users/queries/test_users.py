from uuid import uuid4

import pytest
from faker import Faker

from application.mediator import Mediator
from application.users.commands import CreateUserCommand
from application.users.queries import (
    AuthenticateUserQuery,
    GetUserByIdQuery,
)
from domain.users.entities import UserEntity
from domain.users.exceptions.users import (
    InvalidCredentialsException,
    UserNotFoundException,
)


@pytest.mark.asyncio
async def test_get_user_by_id_success(
    mediator: Mediator,
    faker: Faker,
):
    email = faker.email()
    password = faker.password(length=12)
    name = faker.name()

    user_result, *_ = await mediator.handle_command(
        CreateUserCommand(email=email, password=password, name=name),
    )
    created_user: UserEntity = user_result

    retrieved_user = await mediator.handle_query(
        GetUserByIdQuery(user_id=created_user.oid),
    )

    assert retrieved_user.oid == created_user.oid
    assert retrieved_user.email.as_generic_type() == email
    assert retrieved_user.name.as_generic_type() == name


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(
    mediator: Mediator,
):
    non_existent_id = uuid4()

    with pytest.raises(UserNotFoundException) as exc_info:
        await mediator.handle_query(
            GetUserByIdQuery(user_id=non_existent_id),
        )

    assert exc_info.value.user_id == non_existent_id


@pytest.mark.asyncio
async def test_authenticate_user_query_success(
    mediator: Mediator,
    faker: Faker,
):
    email = faker.email()
    password = faker.password(length=12)
    name = faker.name()

    await mediator.handle_command(
        CreateUserCommand(email=email, password=password, name=name),
    )

    authenticated_user = await mediator.handle_query(
        AuthenticateUserQuery(email=email, password=password),
    )

    assert authenticated_user is not None
    assert authenticated_user.email.as_generic_type() == email
    assert authenticated_user.name.as_generic_type() == name


@pytest.mark.asyncio
async def test_authenticate_user_query_invalid_email(
    mediator: Mediator,
    faker: Faker,
):
    password = faker.password(length=12)

    with pytest.raises(InvalidCredentialsException):
        await mediator.handle_query(
            AuthenticateUserQuery(email="nonexistent@example.com", password=password),
        )


@pytest.mark.asyncio
async def test_authenticate_user_query_invalid_password(
    mediator: Mediator,
    faker: Faker,
):
    email = faker.email()
    password = faker.password(length=12)
    name = faker.name()

    await mediator.handle_command(
        CreateUserCommand(email=email, password=password, name=name),
    )

    with pytest.raises(InvalidCredentialsException):
        await mediator.handle_query(
            AuthenticateUserQuery(email=email, password="wrong_password"),
        )
