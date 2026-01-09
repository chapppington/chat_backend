from dataclasses import dataclass
from datetime import datetime
from typing import Optional

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
    last_online_at: Optional[datetime] = None
