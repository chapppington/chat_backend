from uuid import uuid4

import pytest
from faker import Faker

from application.chats.commands import CreateMessageCommand
from application.mediator import Mediator
from domain.chats.entities.messages import MessageEntity
from domain.chats.exceptions.messages import (
    EmptyMessageContentException,
    MessageContentTooLongException,
)


@pytest.mark.asyncio
async def test_create_message_command_success(
    mediator: Mediator,
    faker: Faker,
):
    chat_id = uuid4()
    sender_id = uuid4()
    content = faker.text(max_nb_chars=100)

    result, *_ = await mediator.handle_command(
        CreateMessageCommand(
            chat_id=chat_id,
            sender_id=sender_id,
            content=content,
        ),
    )

    message: MessageEntity = result

    assert message is not None
    assert message.content.as_generic_type() == content
    assert message.chat_id == chat_id
    assert message.sender_id == sender_id
    assert message.oid is not None


@pytest.mark.asyncio
async def test_create_message_command_empty_content(mediator: Mediator):
    chat_id = uuid4()
    sender_id = uuid4()

    with pytest.raises(EmptyMessageContentException):
        await mediator.handle_command(
            CreateMessageCommand(
                chat_id=chat_id,
                sender_id=sender_id,
                content="",
            ),
        )


@pytest.mark.asyncio
async def test_create_message_command_whitespace_content(mediator: Mediator):
    chat_id = uuid4()
    sender_id = uuid4()

    with pytest.raises(EmptyMessageContentException):
        await mediator.handle_command(
            CreateMessageCommand(
                chat_id=chat_id,
                sender_id=sender_id,
                content="   ",
            ),
        )


@pytest.mark.asyncio
async def test_create_message_command_content_too_long(mediator: Mediator):
    chat_id = uuid4()
    sender_id = uuid4()
    content = "a" * 4097

    with pytest.raises(MessageContentTooLongException) as exc_info:
        await mediator.handle_command(
            CreateMessageCommand(
                chat_id=chat_id,
                sender_id=sender_id,
                content=content,
            ),
        )

    assert exc_info.value.content_length == len(content)
    assert exc_info.value.max_length == 4096
