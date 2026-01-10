from io import BytesIO

from fastapi import (
    FastAPI,
    status,
)
from fastapi.testclient import TestClient

import pytest
from httpx import Response


@pytest.mark.asyncio
async def test_get_current_user_success(
    app: FastAPI,
    authenticated_client: TestClient,
    authenticated_user,
):
    """Тест успешного получения информации о текущем пользователе."""
    url = app.url_path_for("get_current_user")

    response: Response = authenticated_client.get(url=url)

    assert response.is_success
    assert response.status_code == status.HTTP_200_OK

    json_response = response.json()

    assert "data" in json_response
    assert json_response["data"]["oid"] == str(authenticated_user.oid)
    assert json_response["data"]["email"] == authenticated_user.email.as_generic_type()
    assert json_response["data"]["name"] == authenticated_user.name.as_generic_type()
    assert json_response["data"]["avatar_url"] is None


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(
    app: FastAPI,
    client: TestClient,
):
    """Тест получения информации о пользователе без аутентификации."""
    url = app.url_path_for("get_current_user")

    response: Response = client.get(url=url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    json_response = response.json()
    assert "errors" in json_response
    assert len(json_response["errors"]) > 0


@pytest.mark.asyncio
async def test_upload_avatar_success(
    app: FastAPI,
    authenticated_client: TestClient,
    authenticated_user,
):
    """Тест успешной загрузки аватара."""
    url = app.url_path_for("upload_avatar")

    # Create a test image file
    file_content = b"fake image content"
    files = {"file": ("avatar.jpg", BytesIO(file_content), "image/jpeg")}

    response: Response = authenticated_client.post(
        url=url,
        files=files,
    )

    assert response.is_success
    assert response.status_code == status.HTTP_200_OK

    json_response = response.json()

    assert "data" in json_response
    assert json_response["data"]["oid"] == str(authenticated_user.oid)
    assert json_response["data"]["avatar_url"] is not None
    assert "avatars" in json_response["data"]["avatar_url"]
    assert str(authenticated_user.oid) in json_response["data"]["avatar_url"]


@pytest.mark.asyncio
async def test_upload_avatar_unauthorized(
    app: FastAPI,
    client: TestClient,
):
    """Тест загрузки аватара без аутентификации."""
    url = app.url_path_for("upload_avatar")

    file_content = b"fake image content"
    files = {"file": ("avatar.jpg", BytesIO(file_content), "image/jpeg")}

    response: Response = client.post(
        url=url,
        files=files,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    json_response = response.json()
    assert "errors" in json_response
    assert len(json_response["errors"]) > 0


@pytest.mark.asyncio
async def test_upload_avatar_without_file(
    app: FastAPI,
    authenticated_client: TestClient,
):
    """Тест загрузки аватара без файла."""
    url = app.url_path_for("upload_avatar")

    response: Response = authenticated_client.post(url=url)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_upload_avatar_updates_existing(
    app: FastAPI,
    authenticated_client: TestClient,
    authenticated_user,
):
    """Тест обновления существующего аватара."""
    url = app.url_path_for("upload_avatar")

    # Upload first avatar
    file_content_1 = b"first avatar content"
    files_1 = {"file": ("avatar1.jpg", BytesIO(file_content_1), "image/jpeg")}

    response_1: Response = authenticated_client.post(
        url=url,
        files=files_1,
    )

    assert response_1.is_success
    json_response_1 = response_1.json()
    first_avatar_url = json_response_1["data"]["avatar_url"]

    # Upload second avatar
    file_content_2 = b"second avatar content"
    files_2 = {"file": ("avatar2.png", BytesIO(file_content_2), "image/png")}

    response_2: Response = authenticated_client.post(
        url=url,
        files=files_2,
    )

    assert response_2.is_success
    json_response_2 = response_2.json()
    second_avatar_url = json_response_2["data"]["avatar_url"]

    # Avatar URLs should be different (new random filename)
    assert first_avatar_url != second_avatar_url
    assert json_response_2["data"]["oid"] == str(authenticated_user.oid)
