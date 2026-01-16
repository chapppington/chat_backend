from uuid import uuid4

import pytest
from faker import Faker

from application.chats.commands import (
    CreateChatCommand,
    DeleteChatCommand,
)
from application.chats.queries import GetChatByIdQuery
from application.mediator import Mediator
from domain.chats.entities.chats import ChatEntity
from domain.chats.exceptions.chats import (
    ChatAlreadyExistsException,
    ChatNotFoundException,
    ChatTitleTooLongException,
    EmptyChatTitleException,
)


@pytest.mark.asyncio
async def test_create_chat_command_success(
    mediator: Mediator,
    faker: Faker,
):
    title = faker.text(max_nb_chars=50)
    owner_id = uuid4()

    result, *_ = await mediator.handle_command(
        CreateChatCommand(title=title, owner_id=owner_id),
    )

    chat: ChatEntity = result

    assert chat is not None
    assert chat.title.as_generic_type() == title
    assert chat.owner_id == owner_id
    assert chat.oid is not None

    retrieved_chat = await mediator.handle_query(
        GetChatByIdQuery(chat_id=chat.oid),
    )

    assert retrieved_chat.oid == chat.oid
    assert retrieved_chat.title.as_generic_type() == title
    assert retrieved_chat.owner_id == owner_id


@pytest.mark.asyncio
async def test_create_chat_command_empty_title(mediator: Mediator):
    owner_id = uuid4()

    with pytest.raises(EmptyChatTitleException):
        await mediator.handle_command(
            CreateChatCommand(title="", owner_id=owner_id),
        )


@pytest.mark.asyncio
async def test_create_chat_command_whitespace_title(mediator: Mediator):
    owner_id = uuid4()

    with pytest.raises(EmptyChatTitleException):
        await mediator.handle_command(
            CreateChatCommand(title="   ", owner_id=owner_id),
        )


@pytest.mark.asyncio
async def test_create_chat_command_title_too_long(mediator: Mediator):
    title = "a" * 256
    owner_id = uuid4()

    with pytest.raises(ChatTitleTooLongException) as exc_info:
        await mediator.handle_command(
            CreateChatCommand(title=title, owner_id=owner_id),
        )

    assert exc_info.value.title_length == len(title)
    assert exc_info.value.max_length == 255


@pytest.mark.asyncio
async def test_create_chat_command_duplicate_title(
    mediator: Mediator,
    faker: Faker,
):
    title = faker.text(max_nb_chars=50)
    owner_id = uuid4()

    await mediator.handle_command(
        CreateChatCommand(title=title, owner_id=owner_id),
    )

    with pytest.raises(ChatAlreadyExistsException) as exc_info:
        await mediator.handle_command(
            CreateChatCommand(title=title, owner_id=uuid4()),
        )

    assert exc_info.value.title == title


@pytest.mark.asyncio
async def test_delete_chat_command_success(
    mediator: Mediator,
    faker: Faker,
):
    title = faker.text(max_nb_chars=50)
    owner_id = uuid4()

    result, *_ = await mediator.handle_command(
        CreateChatCommand(title=title, owner_id=owner_id),
    )
    created_chat: ChatEntity = result

    await mediator.handle_command(
        DeleteChatCommand(chat_id=created_chat.oid),
    )

    with pytest.raises(ChatNotFoundException) as exc_info:
        await mediator.handle_query(
            GetChatByIdQuery(chat_id=created_chat.oid),
        )

    assert exc_info.value.chat_id == created_chat.oid


@pytest.mark.asyncio
async def test_delete_chat_command_not_found(
    mediator: Mediator,
):
    non_existent_id = uuid4()

    with pytest.raises(ChatNotFoundException) as exc_info:
        await mediator.handle_command(
            DeleteChatCommand(chat_id=non_existent_id),
        )

    assert exc_info.value.chat_id == non_existent_id
