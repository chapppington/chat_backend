from uuid import uuid4

from domain.chats.entities.chats import ChatEntity
from domain.chats.entities.messages import MessageEntity
from domain.chats.value_objects.chats import ChatTitleValueObject
from domain.chats.value_objects.messages import MessageContentValueObject


def test_chat_entity_creation():
    title = ChatTitleValueObject("Test Chat")
    owner_id = uuid4()

    chat = ChatEntity(
        title=title,
        owner_id=owner_id,
    )

    assert chat.title.as_generic_type() == "Test Chat"
    assert chat.owner_id == owner_id
    assert chat.oid is not None
    assert chat.created_at is not None
    assert chat.updated_at is not None
    assert len(chat.messages) == 0


def test_chat_entity_add_message():
    chat_id = uuid4()
    owner_id = uuid4()
    sender_id = uuid4()
    title = ChatTitleValueObject("Test Chat")

    chat = ChatEntity(
        oid=chat_id,
        title=title,
        owner_id=owner_id,
    )

    message = MessageEntity(
        chat_id=chat_id,
        sender_id=sender_id,
        content=MessageContentValueObject("Hello!"),
    )

    assert len(chat.messages) == 0

    chat.add_message(message)

    assert len(chat.messages) == 1
    assert message in chat.messages


def test_chat_entity_add_multiple_messages():
    chat_id = uuid4()
    owner_id = uuid4()
    sender_id = uuid4()
    title = ChatTitleValueObject("Test Chat")

    chat = ChatEntity(
        oid=chat_id,
        title=title,
        owner_id=owner_id,
    )

    message1 = MessageEntity(
        chat_id=chat_id,
        sender_id=sender_id,
        content=MessageContentValueObject("Message 1"),
    )
    message2 = MessageEntity(
        chat_id=chat_id,
        sender_id=sender_id,
        content=MessageContentValueObject("Message 2"),
    )

    chat.add_message(message1)
    chat.add_message(message2)

    assert len(chat.messages) == 2
    assert message1 in chat.messages
    assert message2 in chat.messages
