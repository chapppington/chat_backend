from uuid import uuid4

import pytest
from faker import Faker

from application.chats.commands import (
    CreateChatCommand,
    CreateMessageCommand,
)
from application.chats.queries import GetMessagesQuery
from application.mediator import Mediator


@pytest.mark.asyncio
async def test_get_messages_query_success(
    mediator: Mediator,
    faker: Faker,
):
    title = faker.text(max_nb_chars=50)
    owner_id = uuid4()
    chat_result, *_ = await mediator.handle_command(
        CreateChatCommand(title=title, owner_id=owner_id),
    )
    chat_id = chat_result.oid

    sender_id = uuid4()
    messages_content = [faker.text(max_nb_chars=50) for _ in range(5)]

    for content in messages_content:
        await mediator.handle_command(
            CreateMessageCommand(
                chat_id=chat_id,
                sender_id=sender_id,
                content=content,
            ),
        )

    messages, total = await mediator.handle_query(
        GetMessagesQuery(chat_id=chat_id, limit=10, offset=0),
    )

    assert total == 5
    assert len(list(messages)) == 5


@pytest.mark.asyncio
async def test_get_messages_query_pagination(
    mediator: Mediator,
    faker: Faker,
):
    title = faker.text(max_nb_chars=50)
    owner_id = uuid4()
    chat_result, *_ = await mediator.handle_command(
        CreateChatCommand(title=title, owner_id=owner_id),
    )
    chat_id = chat_result.oid

    sender_id = uuid4()
    messages_content = [faker.text(max_nb_chars=50) for _ in range(10)]

    for content in messages_content:
        await mediator.handle_command(
            CreateMessageCommand(
                chat_id=chat_id,
                sender_id=sender_id,
                content=content,
            ),
        )

    first_page, total = await mediator.handle_query(
        GetMessagesQuery(chat_id=chat_id, limit=3, offset=0),
    )

    assert total == 10
    assert len(list(first_page)) == 3

    second_page, total = await mediator.handle_query(
        GetMessagesQuery(chat_id=chat_id, limit=3, offset=3),
    )

    assert total == 10
    assert len(list(second_page)) == 3


@pytest.mark.asyncio
async def test_get_messages_query_empty_chat(
    mediator: Mediator,
    faker: Faker,
):
    title = faker.text(max_nb_chars=50)
    owner_id = uuid4()
    chat_result, *_ = await mediator.handle_command(
        CreateChatCommand(title=title, owner_id=owner_id),
    )
    chat_id = chat_result.oid

    messages, total = await mediator.handle_query(
        GetMessagesQuery(chat_id=chat_id, limit=10, offset=0),
    )

    assert total == 0
    assert len(list(messages)) == 0


@pytest.mark.asyncio
async def test_get_messages_query_different_chats(
    mediator: Mediator,
    faker: Faker,
):
    title1 = faker.text(max_nb_chars=50)
    owner_id = uuid4()
    chat1_result, *_ = await mediator.handle_command(
        CreateChatCommand(title=title1, owner_id=owner_id),
    )
    chat1_id = chat1_result.oid

    title2 = faker.text(max_nb_chars=50)
    chat2_result, *_ = await mediator.handle_command(
        CreateChatCommand(title=title2, owner_id=owner_id),
    )
    chat2_id = chat2_result.oid

    sender_id = uuid4()

    await mediator.handle_command(
        CreateMessageCommand(
            chat_id=chat1_id,
            sender_id=sender_id,
            content=faker.text(max_nb_chars=50),
        ),
    )

    await mediator.handle_command(
        CreateMessageCommand(
            chat_id=chat1_id,
            sender_id=sender_id,
            content=faker.text(max_nb_chars=50),
        ),
    )

    await mediator.handle_command(
        CreateMessageCommand(
            chat_id=chat2_id,
            sender_id=sender_id,
            content=faker.text(max_nb_chars=50),
        ),
    )

    chat1_messages, chat1_total = await mediator.handle_query(
        GetMessagesQuery(chat_id=chat1_id, limit=10, offset=0),
    )

    chat2_messages, chat2_total = await mediator.handle_query(
        GetMessagesQuery(chat_id=chat2_id, limit=10, offset=0),
    )

    assert chat1_total == 2
    assert len(list(chat1_messages)) == 2
    assert chat2_total == 1
    assert len(list(chat2_messages)) == 1
