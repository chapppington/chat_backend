from abc import (
    ABC,
    abstractmethod,
)
from datetime import datetime
from uuid import UUID

from domain.users.value_objects.relationship_types import RelationshipType


class BaseRelationshipRepository(ABC):
    """Base repository interface for managing user relationships in Neo4j."""

    @abstractmethod
    async def create_user_node(
        self,
        user_id: UUID,
        first_name: str,
        last_name: str,
        city: str | None = None,
    ) -> None:
        """Create a User node in Neo4j."""
        ...

    @abstractmethod
    async def delete_user_node(
        self,
        user_id: UUID,
    ) -> None:
        """Delete a User node from Neo4j."""
        ...

    @abstractmethod
    async def add_friend(
        self,
        user_id: UUID,
        friend_id: UUID,
    ) -> None:
        """Add bidirectional FRIEND relationship between two users."""
        ...

    @abstractmethod
    async def remove_friend(
        self,
        user_id: UUID,
        friend_id: UUID,
    ) -> None:
        """Remove FRIEND relationship between two users."""
        ...

    @abstractmethod
    async def follow_user(
        self,
        user_id: UUID,
        target_id: UUID,
    ) -> None:
        """Create FOLLOWS relationship from user_id to target_id."""
        ...

    @abstractmethod
    async def unfollow_user(
        self,
        user_id: UUID,
        target_id: UUID,
    ) -> None:
        """Remove FOLLOWS relationship."""
        ...

    @abstractmethod
    async def add_relationship(
        self,
        user_id: UUID,
        partner_id: UUID,
        since: datetime | None = None,
    ) -> None:
        """Create IN_RELATIONSHIP_WITH relationship."""
        ...

    @abstractmethod
    async def get_friends(
        self,
        user_id: UUID,
    ) -> list[UUID]:
        """Get list of friend user IDs."""
        ...

    @abstractmethod
    async def get_followers(
        self,
        user_id: UUID,
    ) -> list[UUID]:
        """Get list of follower user IDs."""
        ...

    @abstractmethod
    async def get_following(
        self,
        user_id: UUID,
    ) -> list[UUID]:
        """Get list of users that user_id is following."""
        ...

    @abstractmethod
    async def get_mutual_friends(
        self,
        user_id_1: UUID,
        user_id_2: UUID,
    ) -> list[UUID]:
        """Get mutual friends between two users."""
        ...

    @abstractmethod
    async def check_relationship(
        self,
        user_id: UUID,
        target_id: UUID,
        relationship_type: RelationshipType,
    ) -> bool:
        """Check if relationship exists between two users."""
        ...
