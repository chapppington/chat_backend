from dataclasses import dataclass
from uuid import UUID

from application.base.query import (
    BaseQuery,
    BaseQueryHandler,
)
from domain.users.exceptions.relationships import CannotAddSelfException
from domain.users.interfaces.relationship_repository import BaseRelationshipRepository
from domain.users.value_objects.relationship_types import RelationshipType


@dataclass(frozen=True)
class GetFriendsQuery(BaseQuery):
    """Query to get user's friends."""

    user_id: UUID


@dataclass(frozen=True)
class GetFriendsQueryHandler(
    BaseQueryHandler[GetFriendsQuery, list[UUID]],
):
    relationship_repository: BaseRelationshipRepository

    async def handle(self, query: GetFriendsQuery) -> list[UUID]:
        return await self.relationship_repository.get_friends(query.user_id)


@dataclass(frozen=True)
class GetFollowersQuery(BaseQuery):
    """Query to get user's followers."""

    user_id: UUID


@dataclass(frozen=True)
class GetFollowersQueryHandler(
    BaseQueryHandler[GetFollowersQuery, list[UUID]],
):
    relationship_repository: BaseRelationshipRepository

    async def handle(self, query: GetFollowersQuery) -> list[UUID]:
        return await self.relationship_repository.get_followers(query.user_id)


@dataclass(frozen=True)
class GetFollowingQuery(BaseQuery):
    """Query to get users that user is following."""

    user_id: UUID


@dataclass(frozen=True)
class GetFollowingQueryHandler(
    BaseQueryHandler[GetFollowingQuery, list[UUID]],
):
    relationship_repository: BaseRelationshipRepository

    async def handle(self, query: GetFollowingQuery) -> list[UUID]:
        return await self.relationship_repository.get_following(query.user_id)


@dataclass(frozen=True)
class GetMutualFriendsQuery(BaseQuery):
    """Query to get mutual friends between two users."""

    user_id_1: UUID
    user_id_2: UUID


@dataclass(frozen=True)
class GetMutualFriendsQueryHandler(
    BaseQueryHandler[GetMutualFriendsQuery, list[UUID]],
):
    relationship_repository: BaseRelationshipRepository

    async def handle(self, query: GetMutualFriendsQuery) -> list[UUID]:
        if query.user_id_1 == query.user_id_2:
            raise CannotAddSelfException(
                user_id=query.user_id_1,
                relationship_type="mutual friends",
            )

        return await self.relationship_repository.get_mutual_friends(
            user_id_1=query.user_id_1,
            user_id_2=query.user_id_2,
        )


@dataclass(frozen=True)
class CheckRelationshipQuery(BaseQuery):
    """Query to check if relationship exists."""

    user_id: UUID
    target_id: UUID
    relationship_type: RelationshipType


@dataclass(frozen=True)
class CheckRelationshipQueryHandler(
    BaseQueryHandler[CheckRelationshipQuery, bool],
):
    relationship_repository: BaseRelationshipRepository

    async def handle(self, query: CheckRelationshipQuery) -> bool:
        return await self.relationship_repository.check_relationship(
            user_id=query.user_id,
            target_id=query.target_id,
            relationship_type=query.relationship_type,
        )
