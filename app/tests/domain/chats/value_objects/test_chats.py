import pytest

from domain.chats.exceptions.chats import (
    ChatTitleTooLongException,
    EmptyChatTitleException,
)
from domain.chats.value_objects.chats import ChatTitleValueObject


@pytest.mark.parametrize(
    "title_value,expected",
    [
        ("Test Chat", "Test Chat"),
        ("A", "A"),
        ("A" * 255, "A" * 255),
        ("  Valid Chat  ", "  Valid Chat  "),
    ],
)
def test_chat_title_valid(title_value, expected):
    title = ChatTitleValueObject(title_value)
    assert title.as_generic_type() == expected


@pytest.mark.parametrize(
    "title_value,exception",
    [
        ("", EmptyChatTitleException),
        ("   ", EmptyChatTitleException),
        ("\t", EmptyChatTitleException),
        ("\n", EmptyChatTitleException),
        ("A" * 256, ChatTitleTooLongException),
    ],
)
def test_chat_title_invalid(title_value, exception):
    with pytest.raises(exception):
        ChatTitleValueObject(title_value)
