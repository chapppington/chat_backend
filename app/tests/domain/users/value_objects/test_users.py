import pytest

from domain.users.exceptions import (
    EmptyEmailException,
    EmptyUserNameException,
    InvalidEmailException,
    UserNameTooLongException,
)
from domain.users.value_objects.users import (
    EmailValueObject,
    UserNameValueObject,
)


@pytest.mark.parametrize(
    "email_value,expected",
    [
        ("test@example.com", "test@example.com"),
        ("user.name@domain.co.uk", "user.name@domain.co.uk"),
        ("admin@test.io", "admin@test.io"),
    ],
)
def test_email_valid(email_value, expected):
    email = EmailValueObject(email_value)
    assert email.as_generic_type() == expected


@pytest.mark.parametrize(
    "email_value,exception",
    [
        ("", EmptyEmailException),
        ("invalid-email", InvalidEmailException),
        ("test@", InvalidEmailException),
        ("test@example", InvalidEmailException),
        ("@example.com", InvalidEmailException),
    ],
)
def test_email_invalid(email_value, exception):
    with pytest.raises(exception):
        EmailValueObject(email_value)


@pytest.mark.parametrize(
    "name_value,expected",
    [
        ("John Doe", "John Doe"),
        ("A" * 255, "A" * 255),
        ("Jane Smith", "Jane Smith"),
    ],
)
def test_user_name_valid(name_value, expected):
    name = UserNameValueObject(name_value)
    assert name.as_generic_type() == expected
    assert len(name.as_generic_type()) == len(expected)


@pytest.mark.parametrize(
    "name_value,exception",
    [
        ("", EmptyUserNameException),
        ("A" * 256, UserNameTooLongException),
    ],
)
def test_user_name_invalid(name_value, exception):
    with pytest.raises(exception):
        UserNameValueObject(name_value)
