from pydantic import (
    computed_field,
    Field,
)
from pydantic_settings import BaseSettings


class MongoConfig(BaseSettings):
    """MongoDB configuration settings."""

    mongo_host: str = Field(
        default="localhost",
        alias="MONGO_HOST",
    )

    mongo_port: int = Field(
        default=27017,
        alias="MONGO_PORT",
    )

    mongo_user: str = Field(
        default="admin",
        alias="MONGO_ROOT_USER",
    )

    mongo_password: str = Field(
        default="admin",
        alias="MONGO_ROOT_PASSWORD",
    )

    mongo_database: str = Field(
        default="chat",
        alias="MONGO_DATABASE",
    )

    mongodb_chat_collection: str = Field(
        default="chat",
        alias="MONGODB_CHAT_COLLECTION",
    )
    mongodb_message_collection: str = Field(
        default="message",
        alias="MONGODB_MESSAGE_COLLECTION",
    )

    @computed_field
    @property
    def mongodb_connection_uri(self) -> str:
        """Build MongoDB connection URI from components."""
        if self.mongo_user and self.mongo_password:
            return f"mongodb://{self.mongo_user}:{self.mongo_password}@{self.mongo_host}:{self.mongo_port}/{self.mongo_database}?authSource=admin"
        return f"mongodb://{self.mongo_host}:{self.mongo_port}/{self.mongo_database}"
