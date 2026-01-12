from uuid import UUID

from pydantic import BaseModel

from domain.users.entities import UserEntity


class RegisterRequestSchema(BaseModel):
    email: str
    password: str
    name: str


class LoginRequestSchema(BaseModel):
    email: str
    password: str


class TokenResponseSchema(BaseModel):
    access_token: str
    refresh_token: str


class RefreshTokenResponseSchema(BaseModel):
    access_token: str


class UserResponseSchema(BaseModel):
    oid: UUID
    email: str
    name: str

    @classmethod
    def from_entity(cls, entity: UserEntity) -> "UserResponseSchema":
        return cls(
            oid=entity.oid,
            email=entity.email.as_generic_type(),
            name=entity.name.as_generic_type(),
        )
