from pydantic import Field
from pydantic_settings import BaseSettings


class Neo4jConfig(BaseSettings):
    """Neo4j configuration settings."""

    neo4j_uri: str = Field(
        default="bolt://localhost:7687",
        alias="NEO4J_URI",
    )

    neo4j_user: str = Field(
        default="neo4j",
        alias="NEO4J_USER",
    )

    neo4j_password: str = Field(
        default="password",
        alias="NEO4J_PASSWORD",
    )

    neo4j_database: str = Field(
        default="neo4j",
        alias="NEO4J_DATABASE",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }
