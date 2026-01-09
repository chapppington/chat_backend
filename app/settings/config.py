from pydantic import Field
from pydantic_settings import SettingsConfigDict

from settings.postgres import PostgresConfig


class Config(PostgresConfig):
    """Main application configuration"""

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
