from uuid import uuid4

import pytest
from faker import Faker

from application.chats.commands import CreateChatCommand
from application.chats.queries import GetChatByIdQuery
from application.mediator import Mediator
from domain.chats.entities.chats import ChatEntity
from domain.chats.exceptions.chats import ChatNotFoundException


@pytest.mark.asyncio
async def test_get_chat_by_id_success(
    mediator: Mediator,
    faker: Faker,
):
    title = faker.text(max_nb_chars=50)
    owner_id = uuid4()

    chat_result, *_ = await mediator.handle_command(
        CreateChatCommand(title=title, owner_id=owner_id),
    )
    created_chat: ChatEntity = chat_result

    retrieved_chat = await mediator.handle_query(
        GetChatByIdQuery(chat_id=created_chat.oid),
    )

    assert retrieved_chat.oid == created_chat.oid
    assert retrieved_chat.title.as_generic_type() == title
    assert retrieved_chat.owner_id == owner_id


@pytest.mark.asyncio
async def test_get_chat_by_id_not_found(
    mediator: Mediator,
):
    non_existent_id = uuid4()

    with pytest.raises(ChatNotFoundException) as exc_info:
        await mediator.handle_query(
            GetChatByIdQuery(chat_id=non_existent_id),
        )

    assert exc_info.value.chat_id == non_existent_id
