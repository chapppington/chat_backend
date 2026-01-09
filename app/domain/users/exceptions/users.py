from dataclasses import dataclass
from uuid import UUID

from domain.base.exceptions import DomainException


@dataclass(eq=False)
class UserException(DomainException):
    @property
    def message(self) -> str:
        return "Identity exception occurred"


@dataclass(eq=False)
class EmptyEmailException(UserException):
    @property
    def message(self) -> str:
        return "Email is empty"


@dataclass(eq=False)
class InvalidEmailException(UserException):
    email: str

    @property
    def message(self) -> str:
        return f"Invalid email format: {self.email}"


@dataclass(eq=False)
class EmptyUserNameException(UserException):
    @property
    def message(self) -> str:
        return "User name is empty"


@dataclass(eq=False)
class UserNameTooLongException(UserException):
    name_length: int
    max_length: int

    @property
    def message(self) -> str:
        return (
            f"User name is too long. Current length is {self.name_length}, maximum allowed length is {self.max_length}"
        )


@dataclass(eq=False)
class EmptyPasswordException(UserException):
    @property
    def message(self) -> str:
        return "Password is empty"


@dataclass(eq=False)
class PasswordTooShortException(UserException):
    password_length: int
    min_length: int

    @property
    def message(self) -> str:
        return (
            f"Password is too short. Current length is {self.password_length}, "
            f"minimum required length is {self.min_length}"
        )


@dataclass(eq=False)
class InvalidPasswordException(UserException):
    reason: str

    @property
    def message(self) -> str:
        return f"Invalid password: {self.reason}"


@dataclass(eq=False)
class UserNotFoundException(UserException):
    user_id: UUID

    @property
    def message(self) -> str:
        return f"User with id {self.user_id} not found"


@dataclass(eq=False)
class UserAlreadyExistsException(UserException):
    email: str

    @property
    def message(self) -> str:
        return f"User with email '{self.email}' already exists"


@dataclass(eq=False)
class InvalidCredentialsException(UserException):
    @property
    def message(self) -> str:
        return "Invalid credentials"
