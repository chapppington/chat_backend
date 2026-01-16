"""S3 implementation of file storage interface."""

from io import BytesIO

from infrastructure.s3.client import S3Client

from domain.base.file_storage import BaseFileStorage


class S3FileStorage(BaseFileStorage):
    """S3 implementation of file storage."""

    def __init__(self, s3_client: S3Client) -> None:
        self.s3_client = s3_client

    async def upload_file(self, file_obj: BytesIO, file_path: str) -> None:
        await self.s3_client.upload_fileobj(file_obj, file_path)

    async def delete_file(self, file_path: str) -> None:
        await self.s3_client.delete_file(file_path)

    async def get_file_url(self, file_path: str, expiration: int = 3600) -> str | None:
        try:
            return await self.s3_client.get_presigned_url(file_path, expiration)
        except Exception:
            return None
