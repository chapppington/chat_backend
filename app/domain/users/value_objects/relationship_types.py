from enum import Enum


class RelationshipType(str, Enum):
    """Types of relationships between users."""

    FRIEND = "FRIEND"
    FOLLOWS = "FOLLOWS"
    IN_RELATIONSHIP_WITH = "IN_RELATIONSHIP_WITH"
