from dataclasses import dataclass

from domain.base.entity import BaseEntity
from domain.users.value_objects import (
    EmailValueObject,
    UserNameValueObject,
)


@dataclass(eq=False)
class UserEntity(BaseEntity):
    email: EmailValueObject
    hashed_password: str
    name: UserNameValueObject
