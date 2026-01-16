from dataclasses import dataclass

from domain.base.value_object import BaseValueObject
from domain.chats.exceptions.messages import (
    EmptyMessageContentException,
    MessageContentTooLongException,
)


MAX_MESSAGE_CONTENT_LENGTH = 4096


@dataclass(frozen=True)
class MessageContentValueObject(BaseValueObject):
    value: str

    def validate(self):
        if not self.value or not self.value.strip():
            raise EmptyMessageContentException()

        if len(self.value) > MAX_MESSAGE_CONTENT_LENGTH:
            raise MessageContentTooLongException(
                content_length=len(self.value),
                max_length=MAX_MESSAGE_CONTENT_LENGTH,
            )

    def as_generic_type(self) -> str:
        return str(self.value)
