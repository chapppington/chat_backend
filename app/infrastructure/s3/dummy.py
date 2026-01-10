from io import BytesIO

from domain.base.file_storage import BaseFileStorage


class DummyFileStorage(BaseFileStorage):
    """In-memory file storage for testing."""

    def __init__(self) -> None:
        self._files: dict[str, bytes] = {}

    async def upload_file(self, file_obj: BytesIO, file_path: str) -> None:
        file_obj.seek(0)
        self._files[file_path] = file_obj.read()

    async def delete_file(self, file_path: str) -> None:
        self._files.pop(file_path, None)

    async def get_file_url(self, file_path: str, expiration: int = 3600) -> str | None:
        if file_path in self._files:
            return f"http://test-storage/{file_path}"
        return None
