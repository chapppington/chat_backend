import pytest
from faker import Faker

from application.mediator import Mediator
from application.users.commands import CreateUserCommand
from application.users.queries import GetUserByIdQuery
from domain.users.entities import UserEntity
from domain.users.exceptions.users import (
    EmptyEmailException,
    EmptyPasswordException,
    EmptyUserNameException,
    InvalidEmailException,
    PasswordTooShortException,
    UserAlreadyExistsException,
)


@pytest.mark.asyncio
async def test_create_user_command_success(
    mediator: Mediator,
    faker: Faker,
):
    email = faker.email()
    password = faker.password(length=12)
    name = faker.name()

    result, *_ = await mediator.handle_command(
        CreateUserCommand(email=email, password=password, name=name),
    )

    user: UserEntity = result

    assert user is not None
    assert user.email.as_generic_type() == email
    assert user.name.as_generic_type() == name
    assert user.oid is not None
    assert user.hashed_password is not None

    retrieved_user = await mediator.handle_query(
        GetUserByIdQuery(user_id=user.oid),
    )

    assert retrieved_user.oid == user.oid
    assert retrieved_user.email.as_generic_type() == email


@pytest.mark.asyncio
async def test_create_user_command_empty_email(
    mediator: Mediator,
    faker: Faker,
):
    password = faker.password(length=12)
    name = faker.name()

    with pytest.raises(EmptyEmailException):
        await mediator.handle_command(
            CreateUserCommand(email="", password=password, name=name),
        )


@pytest.mark.asyncio
async def test_create_user_command_invalid_email(
    mediator: Mediator,
    faker: Faker,
):
    password = faker.password(length=12)
    name = faker.name()

    with pytest.raises(InvalidEmailException) as exc_info:
        await mediator.handle_command(
            CreateUserCommand(email="invalid-email", password=password, name=name),
        )

    assert exc_info.value.email == "invalid-email"


@pytest.mark.asyncio
async def test_create_user_command_empty_password(
    mediator: Mediator,
    faker: Faker,
):
    email = faker.email()
    name = faker.name()

    with pytest.raises(EmptyPasswordException):
        await mediator.handle_command(
            CreateUserCommand(email=email, password="", name=name),
        )


@pytest.mark.asyncio
async def test_create_user_command_password_too_short(
    mediator: Mediator,
    faker: Faker,
):
    email = faker.email()
    password = "short"
    name = faker.name()

    with pytest.raises(PasswordTooShortException) as exc_info:
        await mediator.handle_command(
            CreateUserCommand(email=email, password=password, name=name),
        )

    assert exc_info.value.password_length == len(password)


@pytest.mark.asyncio
async def test_create_user_command_empty_name(
    mediator: Mediator,
    faker: Faker,
):
    email = faker.email()
    password = faker.password(length=12)

    with pytest.raises(EmptyUserNameException):
        await mediator.handle_command(
            CreateUserCommand(email=email, password=password, name=""),
        )


@pytest.mark.asyncio
async def test_create_user_command_duplicate_email(
    mediator: Mediator,
    faker: Faker,
):
    email = faker.email()
    password = faker.password(length=12)
    name = faker.name()

    await mediator.handle_command(
        CreateUserCommand(email=email, password=password, name=name),
    )

    with pytest.raises(UserAlreadyExistsException) as exc_info:
        await mediator.handle_command(
            CreateUserCommand(email=email, password=password, name=name),
        )

    assert exc_info.value.email == email
