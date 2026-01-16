from uuid import uuid4

from domain.chats.entities.messages import MessageEntity
from domain.chats.value_objects.messages import MessageContentValueObject


def test_message_entity_creation():
    chat_id = uuid4()
    sender_id = uuid4()
    content = MessageContentValueObject("Hello, world!")

    message = MessageEntity(
        chat_id=chat_id,
        sender_id=sender_id,
        content=content,
    )

    assert message.chat_id == chat_id
    assert message.sender_id == sender_id
    assert message.content.as_generic_type() == "Hello, world!"
    assert message.oid is not None
    assert message.created_at is not None
    assert message.updated_at is not None
