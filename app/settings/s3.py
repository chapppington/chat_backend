from pydantic import Field
from pydantic_settings import BaseSettings


class S3Config(BaseSettings):
    """S3/MinIO configuration settings."""

    s3_endpoint_url: str = Field(
        default="http://localhost:9000",
        alias="S3_ENDPOINT_URL",
    )

    s3_access_key_id: str = Field(
        default="minioadmin",
        alias="S3_ACCESS_KEY_ID",
    )

    s3_secret_access_key: str = Field(
        default="minioadmin",
        alias="S3_SECRET_ACCESS_KEY",
    )

    s3_bucket_name: str = Field(
        default="chat-storage",
        alias="S3_BUCKET_NAME",
    )

    s3_region: str = Field(
        default="us-east-1",
        alias="S3_REGION",
    )

    s3_use_ssl: bool = Field(
        default=False,
        alias="S3_USE_SSL",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }
