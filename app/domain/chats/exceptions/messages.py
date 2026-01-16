from dataclasses import dataclass
from uuid import UUID

from domain.base.exceptions import DomainException


@dataclass(eq=False)
class MessageException(DomainException):
    @property
    def message(self) -> str:
        return "Message exception occurred"


@dataclass(eq=False)
class EmptyMessageContentException(MessageException):
    @property
    def message(self) -> str:
        return "Message content is empty"


@dataclass(eq=False)
class MessageContentTooLongException(MessageException):
    content_length: int
    max_length: int

    @property
    def message(self) -> str:
        return (
            f"Message content is too long. Current length is {self.content_length}, "
            f"maximum allowed length is {self.max_length}"
        )


@dataclass(eq=False)
class MessageNotFoundException(MessageException):
    message_id: UUID

    @property
    def message(self) -> str:
        return f"Message with id {self.message_id} not found"
