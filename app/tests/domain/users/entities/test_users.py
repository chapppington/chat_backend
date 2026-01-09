from datetime import datetime
from uuid import uuid4

from domain.users.entities import UserEntity
from domain.users.value_objects import (
    EmailValueObject,
    UserNameValueObject,
)


def test_user_entity_creation():
    email = EmailValueObject("test@example.com")
    name = UserNameValueObject("Test User")
    password = "hashed_password_123"

    user = UserEntity(
        email=email,
        hashed_password=password,
        name=name,
    )

    assert user.email.as_generic_type() == "test@example.com"
    assert user.hashed_password == password
    assert user.name.as_generic_type() == "Test User"
    assert user.oid is not None
    assert user.created_at is not None
    assert user.updated_at is not None
    assert user.last_online_at is None


def test_user_entity_equality():
    user_id = uuid4()
    email1 = EmailValueObject("test@example.com")
    email2 = EmailValueObject("test@example.com")
    email3 = EmailValueObject("other@example.com")
    name = UserNameValueObject("Test User")

    user1 = UserEntity(oid=user_id, email=email1, hashed_password="hash1", name=name)
    user2 = UserEntity(oid=user_id, email=email2, hashed_password="hash2", name=name)
    user3 = UserEntity(oid=uuid4(), email=email3, hashed_password="hash1", name=name)

    assert user1 == user2
    assert user1 != user3


def test_user_entity_hash():
    user_id = uuid4()
    email1 = EmailValueObject("test@example.com")
    email2 = EmailValueObject("test@example.com")
    name = UserNameValueObject("Test User")

    user1 = UserEntity(oid=user_id, email=email1, hashed_password="hash1", name=name)
    user2 = UserEntity(oid=user_id, email=email2, hashed_password="hash2", name=name)

    assert hash(user1) == hash(user2)


def test_user_entity_creation_without_last_online_at():
    """Тест создания пользователя без указания last_online_at."""
    email = EmailValueObject("test@example.com")
    name = UserNameValueObject("Test User")
    password = "hashed_password_123"

    user = UserEntity(
        email=email,
        hashed_password=password,
        name=name,
    )

    assert user.last_online_at is None


def test_user_entity_creation_with_last_online_at():
    """Тест создания пользователя с указанием last_online_at."""
    email = EmailValueObject("test@example.com")
    name = UserNameValueObject("Test User")
    password = "hashed_password_123"
    last_online = datetime(2024, 1, 15, 12, 30, 0)

    user = UserEntity(
        email=email,
        hashed_password=password,
        name=name,
        last_online_at=last_online,
    )

    assert user.last_online_at == last_online
    assert user.last_online_at is not None


def test_user_entity_last_online_at_update():
    """Тест обновления поля last_online_at."""
    email = EmailValueObject("test@example.com")
    name = UserNameValueObject("Test User")
    password = "hashed_password_123"

    user = UserEntity(
        email=email,
        hashed_password=password,
        name=name,
    )

    assert user.last_online_at is None

    # Обновляем last_online_at
    new_last_online = datetime.now()
    user.last_online_at = new_last_online

    assert user.last_online_at == new_last_online
    assert user.last_online_at is not None


def test_user_entity_last_online_at_can_be_set_to_none():
    """Тест что last_online_at можно установить в None."""
    email = EmailValueObject("test@example.com")
    name = UserNameValueObject("Test User")
    password = "hashed_password_123"
    last_online = datetime(2024, 1, 15, 12, 30, 0)

    user = UserEntity(
        email=email,
        hashed_password=password,
        name=name,
        last_online_at=last_online,
    )

    assert user.last_online_at == last_online

    # Устанавливаем обратно в None
    user.last_online_at = None

    assert user.last_online_at is None
