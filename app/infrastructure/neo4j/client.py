from contextlib import asynccontextmanager
from typing import (
    Any,
    AsyncGenerator,
)

from neo4j import (
    AsyncGraphDatabase,
    AsyncSession,
    AsyncTransaction,
)

from settings.config import Config


class Neo4jClient:
    """Neo4j database client for managing graph relationships."""

    def __init__(self, config: Config) -> None:
        self._driver = AsyncGraphDatabase.driver(
            config.neo4j_uri,
            auth=(config.neo4j_user, config.neo4j_password),
        )
        self._database = config.neo4j_database

    async def close(self) -> None:
        """Close the Neo4j driver connection."""
        await self._driver.close()

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, Any]:
        """Get an async Neo4j session."""
        session = self._driver.session(database=self._database)
        try:
            yield session
        finally:
            await session.close()

    @asynccontextmanager
    async def get_transaction(self) -> AsyncGenerator[AsyncTransaction, Any]:
        """Get an async Neo4j transaction."""
        async with self.get_session() as session:
            async with session.begin_transaction() as transaction:
                yield transaction
