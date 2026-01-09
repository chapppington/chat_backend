import re
from dataclasses import dataclass

from domain.base.value_object import BaseValueObject
from domain.users.exceptions import (
    EmptyEmailException,
    EmptyUserNameException,
    InvalidEmailException,
    UserNameTooLongException,
)


MIN_USER_NAME_LENGTH = 3
MAX_USER_NAME_LENGTH = 255


@dataclass(frozen=True)
class EmailValueObject(BaseValueObject):
    value: str

    def validate(self):
        if not self.value:
            raise EmptyEmailException()

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, self.value):
            raise InvalidEmailException(email=self.value)

    def as_generic_type(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class UserNameValueObject(BaseValueObject):
    value: str

    def validate(self):
        if not self.value:
            raise EmptyUserNameException()

        if len(self.value) > MAX_USER_NAME_LENGTH:
            raise UserNameTooLongException(
                name_length=len(self.value),
                max_length=MAX_USER_NAME_LENGTH,
            )

    def as_generic_type(self) -> str:
        return str(self.value)
