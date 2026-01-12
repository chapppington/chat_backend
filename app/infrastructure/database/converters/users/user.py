from infrastructure.database.models.users.user import UserModel

from domain.users.entities.users import UserEntity
from domain.users.value_objects.users import (
    EmailValueObject,
    UserNameValueObject,
)


def user_entity_to_model(entity: UserEntity) -> UserModel:
    return UserModel(
        oid=entity.oid,
        email=entity.email.as_generic_type(),
        hashed_password=entity.hashed_password,
        name=entity.name.as_generic_type(),
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def user_model_to_entity(model: UserModel) -> UserEntity:
    return UserEntity(
        oid=model.oid,
        email=EmailValueObject(value=model.email),
        hashed_password=model.hashed_password,
        name=UserNameValueObject(value=model.name),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
