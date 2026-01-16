from dataclasses import dataclass
from uuid import UUID

from domain.base.exceptions import DomainException


@dataclass(eq=False)
class ChatException(DomainException):
    @property
    def message(self) -> str:
        return "Chat exception occurred"


@dataclass(eq=False)
class EmptyChatTitleException(ChatException):
    @property
    def message(self) -> str:
        return "Chat title is empty"


@dataclass(eq=False)
class ChatTitleTooLongException(ChatException):
    title_length: int
    max_length: int

    @property
    def message(self) -> str:
        return (
            f"Chat title is too long. Current length is {self.title_length}, "
            f"maximum allowed length is {self.max_length}"
        )


@dataclass(eq=False)
class ChatNotFoundException(ChatException):
    chat_id: UUID

    @property
    def message(self) -> str:
        return f"Chat with id {self.chat_id} not found"


@dataclass(eq=False)
class ChatAlreadyExistsException(ChatException):
    title: str

    @property
    def message(self) -> str:
        return f"Chat with title '{self.title}' already exists"
