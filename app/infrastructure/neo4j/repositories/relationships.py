from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from infrastructure.neo4j.client import Neo4jClient

from domain.users.interfaces.relationship_repository import BaseRelationshipRepository
from domain.users.value_objects.relationship_types import RelationshipType


@dataclass
class Neo4jRelationshipRepository(BaseRelationshipRepository):
    """Neo4j implementation of relationship repository."""

    neo4j_client: Neo4jClient

    async def create_user_node(
        self,
        user_id: UUID,
        first_name: str,
        last_name: str,
        city: str | None = None,
    ) -> None:
        """Create a User node in Neo4j."""
        async with self.neo4j_client.get_session() as session:
            query = """
            MERGE (u:User {user_id: $user_id})
            SET u.first_name = $first_name,
                u.last_name = $last_name,
                u.city = $city
            """
            await session.run(
                query,
                user_id=str(user_id),
                first_name=first_name,
                last_name=last_name,
                city=city or "",
            )

    async def delete_user_node(
        self,
        user_id: UUID,
    ) -> None:
        """Delete a User node from Neo4j."""
        async with self.neo4j_client.get_session() as session:
            query = """
            MATCH (u:User {user_id: $user_id})
            DETACH DELETE u
            """
            await session.run(query, user_id=str(user_id))

    async def add_friend(
        self,
        user_id: UUID,
        friend_id: UUID,
    ) -> None:
        """Add bidirectional FRIEND relationship between two users."""
        async with self.neo4j_client.get_session() as session:
            query = """
            MATCH (u1:User {user_id: $user_id})
            MATCH (u2:User {user_id: $friend_id})
            MERGE (u1)-[:FRIEND]->(u2)
            MERGE (u2)-[:FRIEND]->(u1)
            """
            await session.run(
                query,
                user_id=str(user_id),
                friend_id=str(friend_id),
            )

    async def remove_friend(
        self,
        user_id: UUID,
        friend_id: UUID,
    ) -> None:
        """Remove FRIEND relationship between two users."""
        async with self.neo4j_client.get_session() as session:
            query = """
            MATCH (u1:User {user_id: $user_id})-[r1:FRIEND]->(u2:User {user_id: $friend_id})
            MATCH (u2)-[r2:FRIEND]->(u1)
            DELETE r1, r2
            """
            await session.run(
                query,
                user_id=str(user_id),
                friend_id=str(friend_id),
            )

    async def follow_user(
        self,
        user_id: UUID,
        target_id: UUID,
    ) -> None:
        """Create FOLLOWS relationship from user_id to target_id."""
        async with self.neo4j_client.get_session() as session:
            query = """
            MATCH (u1:User {user_id: $user_id})
            MATCH (u2:User {user_id: $target_id})
            MERGE (u1)-[:FOLLOWS]->(u2)
            """
            await session.run(
                query,
                user_id=str(user_id),
                target_id=str(target_id),
            )

    async def unfollow_user(
        self,
        user_id: UUID,
        target_id: UUID,
    ) -> None:
        """Remove FOLLOWS relationship."""
        async with self.neo4j_client.get_session() as session:
            query = """
            MATCH (u1:User {user_id: $user_id})-[r:FOLLOWS]->(u2:User {user_id: $target_id})
            DELETE r
            """
            await session.run(
                query,
                user_id=str(user_id),
                target_id=str(target_id),
            )

    async def add_relationship(
        self,
        user_id: UUID,
        partner_id: UUID,
        since: datetime | None = None,
    ) -> None:
        """Create IN_RELATIONSHIP_WITH relationship."""
        async with self.neo4j_client.get_session() as session:
            query = """
            MATCH (u1:User {user_id: $user_id})
            MATCH (u2:User {user_id: $partner_id})
            MERGE (u1)-[r:IN_RELATIONSHIP_WITH]->(u2)
            SET r.since = $since
            """
            await session.run(
                query,
                user_id=str(user_id),
                partner_id=str(partner_id),
                since=since.isoformat() if since else None,
            )

    async def get_friends(
        self,
        user_id: UUID,
    ) -> list[UUID]:
        """Get list of friend user IDs."""
        async with self.neo4j_client.get_session() as session:
            query = """
            MATCH (u:User {user_id: $user_id})-[:FRIEND]->(f:User)
            RETURN f.user_id as friend_id
            """
            result = await session.run(query, user_id=str(user_id))
            records = await result.values()
            return [UUID(record[0]) for record in records]

    async def get_followers(
        self,
        user_id: UUID,
    ) -> list[UUID]:
        """Get list of follower user IDs."""
        async with self.neo4j_client.get_session() as session:
            query = """
            MATCH (f:User)-[:FOLLOWS]->(u:User {user_id: $user_id})
            RETURN f.user_id as follower_id
            """
            result = await session.run(query, user_id=str(user_id))
            records = await result.values()
            return [UUID(record[0]) for record in records]

    async def get_following(
        self,
        user_id: UUID,
    ) -> list[UUID]:
        """Get list of users that user_id is following."""
        async with self.neo4j_client.get_session() as session:
            query = """
            MATCH (u:User {user_id: $user_id})-[:FOLLOWS]->(f:User)
            RETURN f.user_id as following_id
            """
            result = await session.run(query, user_id=str(user_id))
            records = await result.values()
            return [UUID(record[0]) for record in records]

    async def get_mutual_friends(
        self,
        user_id_1: UUID,
        user_id_2: UUID,
    ) -> list[UUID]:
        """Get mutual friends between two users."""
        async with self.neo4j_client.get_session() as session:
            query = """
            MATCH (u1:User {user_id: $user_id_1})-[:FRIEND]->(mutual:User)<-[:FRIEND]-(u2:User {user_id: $user_id_2})
            RETURN mutual.user_id as mutual_friend_id
            """
            result = await session.run(
                query,
                user_id_1=str(user_id_1),
                user_id_2=str(user_id_2),
            )
            records = await result.values()
            return [UUID(record[0]) for record in records]

    async def check_relationship(
        self,
        user_id: UUID,
        target_id: UUID,
        relationship_type: RelationshipType,
    ) -> bool:
        """Check if relationship exists between two users."""
        async with self.neo4j_client.get_session() as session:
            rel_type = relationship_type.value
            query = f"""
            MATCH (u1:User {{user_id: $user_id}})-[r:{rel_type}]->(u2:User {{user_id: $target_id}})
            RETURN count(r) > 0 as exists
            """
            result = await session.run(
                query,
                user_id=str(user_id),
                target_id=str(target_id),
            )
            record = await result.single()
            return record["exists"] if record else False
