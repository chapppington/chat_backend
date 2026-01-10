"""S3 client for MinIO integration."""

from contextlib import asynccontextmanager

import aioboto3
from botocore.exceptions import ClientError

from settings.config import Config


class S3Client:
    """Async S3 client wrapper for MinIO."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.session = aioboto3.Session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.client(
            "s3",
            endpoint_url=self.config.s3_endpoint_url,
            aws_access_key_id=self.config.s3_access_key_id,
            aws_secret_access_key=self.config.s3_secret_access_key,
            region_name=self.config.s3_region,
            use_ssl=self.config.s3_use_ssl,
        ) as client:
            yield client

    async def create_bucket_if_not_exists(self) -> None:
        """Create bucket if it doesn't exist."""
        async with self.get_client() as client:
            try:
                await client.head_bucket(Bucket=self.config.s3_bucket_name)
            except ClientError:
                await client.create_bucket(Bucket=self.config.s3_bucket_name)

    async def upload_file(self, file_path: str, object_name: str) -> None:
        async with self.get_client() as client:
            await self.create_bucket_if_not_exists()
            await client.upload_file(file_path, self.config.s3_bucket_name, object_name)

    async def upload_fileobj(self, file_obj, object_name: str) -> None:
        async with self.get_client() as client:
            await self.create_bucket_if_not_exists()
            await client.upload_fileobj(file_obj, self.config.s3_bucket_name, object_name)

    async def download_file(self, object_name: str, file_path: str) -> None:
        async with self.get_client() as client:
            await client.download_file(self.config.s3_bucket_name, object_name, file_path)

    async def download_fileobj(self, object_name: str, file_obj) -> None:
        async with self.get_client() as client:
            await client.download_fileobj(self.config.s3_bucket_name, object_name, file_obj)

    async def delete_file(self, object_name: str) -> None:
        async with self.get_client() as client:
            await client.delete_object(Bucket=self.config.s3_bucket_name, Key=object_name)

    async def get_presigned_url(self, object_name: str, expiration: int = 3600) -> str:
        async with self.get_client() as client:
            return await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.config.s3_bucket_name, "Key": object_name},
                ExpiresIn=expiration,
            )

    async def list_objects(self, prefix: str = "") -> list[str]:
        async with self.get_client() as client:
            response = await client.list_objects_v2(
                Bucket=self.config.s3_bucket_name,
                Prefix=prefix,
            )
            if "Contents" not in response:
                return []
            return [obj["Key"] for obj in response["Contents"]]
