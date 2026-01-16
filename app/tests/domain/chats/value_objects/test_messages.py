import pytest

from domain.chats.exceptions.messages import (
    EmptyMessageContentException,
    MessageContentTooLongException,
)
from domain.chats.value_objects.messages import MessageContentValueObject


@pytest.mark.parametrize(
    "content_value,expected",
    [
        ("Hello, world!", "Hello, world!"),
        ("A", "A"),
        ("A" * 4096, "A" * 4096),
        ("  Valid message  ", "  Valid message  "),
        ("Multi\nline\nmessage", "Multi\nline\nmessage"),
    ],
)
def test_message_content_valid(content_value, expected):
    content = MessageContentValueObject(content_value)
    assert content.as_generic_type() == expected


@pytest.mark.parametrize(
    "content_value,exception",
    [
        ("", EmptyMessageContentException),
        ("   ", EmptyMessageContentException),
        ("\t", EmptyMessageContentException),
        ("\n", EmptyMessageContentException),
        ("A" * 4097, MessageContentTooLongException),
    ],
)
def test_message_content_invalid(content_value, exception):
    with pytest.raises(exception):
        MessageContentValueObject(content_value)
