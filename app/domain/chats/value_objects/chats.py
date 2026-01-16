from dataclasses import dataclass

from domain.base.value_object import BaseValueObject
from domain.chats.exceptions.chats import (
    ChatTitleTooLongException,
    EmptyChatTitleException,
)


MIN_CHAT_TITLE_LENGTH = 1
MAX_CHAT_TITLE_LENGTH = 255


@dataclass(frozen=True)
class ChatTitleValueObject(BaseValueObject):
    value: str

    def validate(self):
        if not self.value or not self.value.strip():
            raise EmptyChatTitleException()

        if len(self.value) > MAX_CHAT_TITLE_LENGTH:
            raise ChatTitleTooLongException(
                title_length=len(self.value),
                max_length=MAX_CHAT_TITLE_LENGTH,
            )

    def as_generic_type(self) -> str:
        return str(self.value)
