from pydantic import Field
from pydantic_settings import SettingsConfigDict

from settings.mongo import MongoConfig
from settings.postgres import PostgresConfig
from settings.s3 import S3Config


class Config(PostgresConfig, S3Config, MongoConfig):
    """Main application configuration."""

    jwt_secret_key: str = Field(
        alias="JWT_SECRET_KEY",
        default="secret-key",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
