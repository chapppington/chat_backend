from pydantic import Field
from pydantic_settings import BaseSettings


class KafkaConfig(BaseSettings):
    """Kafka configuration settings."""

    kafka_url: str = Field(
        default="localhost:29092",
        alias="KAFKA_URL",
    )

    kafka_topic_prefix: str = Field(
        default="chat",
        alias="KAFKA_TOPIC_PREFIX",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }
