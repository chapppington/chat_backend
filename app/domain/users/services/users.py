import re
from dataclasses import dataclass
from uuid import UUID

import bcrypt

from domain.users.entities import UserEntity
from domain.users.exceptions import (
    EmptyPasswordException,
    InvalidCredentialsException,
    InvalidPasswordException,
    PasswordTooShortException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from domain.users.interfaces.repository import BaseUserRepository
from domain.users.value_objects import (
    EmailValueObject,
    UserNameValueObject,
)


MIN_PASSWORD_LENGTH = 8


@dataclass
class UserService:
    user_repository: BaseUserRepository

    def _validate_password(self, password: str) -> None:
        if not password:
            raise EmptyPasswordException()

        if len(password) < MIN_PASSWORD_LENGTH:
            raise PasswordTooShortException(
                password_length=len(password),
                min_length=MIN_PASSWORD_LENGTH,
            )

        has_letter = bool(re.search(r"[a-zA-Z]", password))
        has_digit = bool(re.search(r"\d", password))

        if not (has_letter and has_digit):
            raise InvalidPasswordException(
                reason="Password must contain at least one letter and one digit",
            )

    async def create_user(
        self,
        email: str,
        password: str,
        name: str,
    ) -> UserEntity:
        existing_user = await self.user_repository.get_by_email(email)

        if existing_user:
            raise UserAlreadyExistsException(email=email)

        self._validate_password(password)

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(rounds=8),
        ).decode("utf-8")

        user = UserEntity(
            email=EmailValueObject(email),
            hashed_password=hashed_password,
            name=UserNameValueObject(name),
        )

        await self.user_repository.add(user)

        return user

    async def get_by_id(
        self,
        user_id: UUID,
    ) -> UserEntity:
        user = await self.user_repository.get_by_id(user_id)

        if not user:
            raise UserNotFoundException(user_id=user_id)

        return user

    async def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> UserEntity:
        user = await self.user_repository.get_by_email(email)

        if user:
            password_valid = bcrypt.checkpw(
                password.encode("utf-8"),
                user.hashed_password.encode("utf-8"),
            )

        if not user or not password_valid:
            raise InvalidCredentialsException()

        return user
