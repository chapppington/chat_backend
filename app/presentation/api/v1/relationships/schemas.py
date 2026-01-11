from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class RelationshipResponseSchema(BaseModel):
    """Schema for relationship response."""

    user_id: UUID
    target_id: UUID
    relationship_type: str
    created_at: Optional[datetime] = None


class FriendsListResponseSchema(BaseModel):
    """Schema for friends list response."""

    friends: list[UUID]


class FollowersListResponseSchema(BaseModel):
    """Schema for followers list response."""

    followers: list[UUID]


class FollowingListResponseSchema(BaseModel):
    """Schema for following list response."""

    following: list[UUID]


class MutualFriendsResponseSchema(BaseModel):
    """Schema for mutual friends response."""

    mutual_friends: list[UUID]


class AddRelationshipRequestSchema(BaseModel):
    """Schema for adding a relationship."""

    since: Optional[datetime] = None
