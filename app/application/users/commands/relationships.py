from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from application.base.command import (
    BaseCommand,
    BaseCommandHandler,
)
from domain.users.exceptions.relationships import CannotAddSelfException
from domain.users.interfaces.relationship_repository import BaseRelationshipRepository
from domain.users.value_objects.relationship_types import RelationshipType


@dataclass(frozen=True)
class AddFriendCommand(BaseCommand):
    """Command to add a friend relationship."""

    user_id: UUID
    friend_id: UUID


@dataclass(frozen=True)
class AddFriendCommandHandler(
    BaseCommandHandler[AddFriendCommand, None],
):
    relationship_repository: BaseRelationshipRepository

    async def handle(self, command: AddFriendCommand) -> None:
        if command.user_id == command.friend_id:
            raise CannotAddSelfException(
                user_id=command.user_id,
                relationship_type=RelationshipType.FRIEND.value,
            )

        await self.relationship_repository.add_friend(
            user_id=command.user_id,
            friend_id=command.friend_id,
        )


@dataclass(frozen=True)
class RemoveFriendCommand(BaseCommand):
    """Command to remove a friend relationship."""

    user_id: UUID
    friend_id: UUID


@dataclass(frozen=True)
class RemoveFriendCommandHandler(
    BaseCommandHandler[RemoveFriendCommand, None],
):
    relationship_repository: BaseRelationshipRepository

    async def handle(self, command: RemoveFriendCommand) -> None:
        await self.relationship_repository.remove_friend(
            user_id=command.user_id,
            friend_id=command.friend_id,
        )


@dataclass(frozen=True)
class FollowUserCommand(BaseCommand):
    """Command to follow a user."""

    user_id: UUID
    target_id: UUID


@dataclass(frozen=True)
class FollowUserCommandHandler(
    BaseCommandHandler[FollowUserCommand, None],
):
    relationship_repository: BaseRelationshipRepository

    async def handle(self, command: FollowUserCommand) -> None:
        if command.user_id == command.target_id:
            raise CannotAddSelfException(
                user_id=command.user_id,
                relationship_type=RelationshipType.FOLLOWS.value,
            )

        await self.relationship_repository.follow_user(
            user_id=command.user_id,
            target_id=command.target_id,
        )


@dataclass(frozen=True)
class UnfollowUserCommand(BaseCommand):
    """Command to unfollow a user."""

    user_id: UUID
    target_id: UUID


@dataclass(frozen=True)
class UnfollowUserCommandHandler(
    BaseCommandHandler[UnfollowUserCommand, None],
):
    relationship_repository: BaseRelationshipRepository

    async def handle(self, command: UnfollowUserCommand) -> None:
        await self.relationship_repository.unfollow_user(
            user_id=command.user_id,
            target_id=command.target_id,
        )


@dataclass(frozen=True)
class AddRelationshipCommand(BaseCommand):
    """Command to add a romantic relationship."""

    user_id: UUID
    partner_id: UUID
    since: datetime | None = None


@dataclass(frozen=True)
class AddRelationshipCommandHandler(
    BaseCommandHandler[AddRelationshipCommand, None],
):
    relationship_repository: BaseRelationshipRepository

    async def handle(self, command: AddRelationshipCommand) -> None:
        if command.user_id == command.partner_id:
            raise CannotAddSelfException(
                user_id=command.user_id,
                relationship_type=RelationshipType.IN_RELATIONSHIP_WITH.value,
            )

        await self.relationship_repository.add_relationship(
            user_id=command.user_id,
            partner_id=command.partner_id,
            since=command.since,
        )
