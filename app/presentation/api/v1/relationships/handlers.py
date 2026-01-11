from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    status,
)

from presentation.api.dependencies import get_current_user_id
from presentation.api.schemas import (
    ApiResponse,
    ErrorResponseSchema,
)
from presentation.api.v1.relationships.schemas import (
    AddRelationshipRequestSchema,
    FollowersListResponseSchema,
    FollowingListResponseSchema,
    FriendsListResponseSchema,
    MutualFriendsResponseSchema,
    RelationshipResponseSchema,
)

from application.container import init_container
from application.mediator import Mediator
from application.users.commands import (
    AddFriendCommand,
    AddRelationshipCommand,
    FollowUserCommand,
    RemoveFriendCommand,
    UnfollowUserCommand,
)
from application.users.queries import (
    GetFollowersQuery,
    GetFollowingQuery,
    GetFriendsQuery,
    GetMutualFriendsQuery,
)
from domain.users.value_objects.relationship_types import RelationshipType


router = APIRouter(prefix="/relationships", tags=["relationships"])


@router.post(
    "/friends/{friend_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[RelationshipResponseSchema],
    responses={
        status.HTTP_201_CREATED: {"model": ApiResponse[RelationshipResponseSchema]},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponseSchema},
    },
)
async def add_friend(
    friend_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    container=Depends(init_container),
) -> ApiResponse[RelationshipResponseSchema]:
    """Добавить пользователя в друзья."""
    mediator: Mediator = container.resolve(Mediator)

    command = AddFriendCommand(user_id=user_id, friend_id=friend_id)
    await mediator.handle_command(command)

    return ApiResponse[RelationshipResponseSchema](
        data=RelationshipResponseSchema(
            user_id=user_id,
            target_id=friend_id,
            relationship_type=RelationshipType.FRIEND.value,
        ),
    )


@router.delete(
    "/friends/{friend_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[None],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[None]},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponseSchema},
    },
)
async def remove_friend(
    friend_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    container=Depends(init_container),
) -> ApiResponse[None]:
    """Удалить пользователя из друзей."""
    mediator: Mediator = container.resolve(Mediator)

    command = RemoveFriendCommand(user_id=user_id, friend_id=friend_id)
    await mediator.handle_command(command)

    return ApiResponse[None](data=None)


@router.post(
    "/follow/{target_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[RelationshipResponseSchema],
    responses={
        status.HTTP_201_CREATED: {"model": ApiResponse[RelationshipResponseSchema]},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponseSchema},
    },
)
async def follow_user(
    target_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    container=Depends(init_container),
) -> ApiResponse[RelationshipResponseSchema]:
    """Подписаться на пользователя."""
    mediator: Mediator = container.resolve(Mediator)

    command = FollowUserCommand(user_id=user_id, target_id=target_id)
    await mediator.handle_command(command)

    return ApiResponse[RelationshipResponseSchema](
        data=RelationshipResponseSchema(
            user_id=user_id,
            target_id=target_id,
            relationship_type=RelationshipType.FOLLOWS.value,
        ),
    )


@router.delete(
    "/follow/{target_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[None],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[None]},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponseSchema},
    },
)
async def unfollow_user(
    target_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    container=Depends(init_container),
) -> ApiResponse[None]:
    """Отписаться от пользователя."""
    mediator: Mediator = container.resolve(Mediator)

    command = UnfollowUserCommand(user_id=user_id, target_id=target_id)
    await mediator.handle_command(command)

    return ApiResponse[None](data=None)


@router.post(
    "/relationship/{partner_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[RelationshipResponseSchema],
    responses={
        status.HTTP_201_CREATED: {"model": ApiResponse[RelationshipResponseSchema]},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponseSchema},
    },
)
async def add_relationship(
    partner_id: UUID,
    request: AddRelationshipRequestSchema,
    user_id: UUID = Depends(get_current_user_id),
    container=Depends(init_container),
) -> ApiResponse[RelationshipResponseSchema]:
    """Добавить романтические отношения с пользователем."""
    mediator: Mediator = container.resolve(Mediator)

    command = AddRelationshipCommand(
        user_id=user_id,
        partner_id=partner_id,
        since=request.since,
    )
    await mediator.handle_command(command)

    return ApiResponse[RelationshipResponseSchema](
        data=RelationshipResponseSchema(
            user_id=user_id,
            target_id=partner_id,
            relationship_type=RelationshipType.IN_RELATIONSHIP_WITH.value,
            created_at=request.since,
        ),
    )


@router.get(
    "/friends",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[FriendsListResponseSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[FriendsListResponseSchema]},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema},
    },
)
async def get_friends(
    user_id: UUID = Depends(get_current_user_id),
    container=Depends(init_container),
) -> ApiResponse[FriendsListResponseSchema]:
    """Получить список друзей текущего пользователя."""
    mediator: Mediator = container.resolve(Mediator)

    query = GetFriendsQuery(user_id=user_id)
    friends = await mediator.handle_query(query)

    return ApiResponse[FriendsListResponseSchema](
        data=FriendsListResponseSchema(friends=friends),
    )


@router.get(
    "/followers",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[FollowersListResponseSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[FollowersListResponseSchema]},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema},
    },
)
async def get_followers(
    user_id: UUID = Depends(get_current_user_id),
    container=Depends(init_container),
) -> ApiResponse[FollowersListResponseSchema]:
    """Получить список подписчиков текущего пользователя."""
    mediator: Mediator = container.resolve(Mediator)

    query = GetFollowersQuery(user_id=user_id)
    followers = await mediator.handle_query(query)

    return ApiResponse[FollowersListResponseSchema](
        data=FollowersListResponseSchema(followers=followers),
    )


@router.get(
    "/following",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[FollowingListResponseSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[FollowingListResponseSchema]},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema},
    },
)
async def get_following(
    user_id: UUID = Depends(get_current_user_id),
    container=Depends(init_container),
) -> ApiResponse[FollowingListResponseSchema]:
    """Получить список пользователей, на которых подписан текущий
    пользователь."""
    mediator: Mediator = container.resolve(Mediator)

    query = GetFollowingQuery(user_id=user_id)
    following = await mediator.handle_query(query)

    return ApiResponse[FollowingListResponseSchema](
        data=FollowingListResponseSchema(following=following),
    )


@router.get(
    "/mutual/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[MutualFriendsResponseSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[MutualFriendsResponseSchema]},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponseSchema},
    },
)
async def get_mutual_friends(
    user_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    container=Depends(init_container),
) -> ApiResponse[MutualFriendsResponseSchema]:
    """Получить список общих друзей между текущим пользователем и указанным."""
    mediator: Mediator = container.resolve(Mediator)

    query = GetMutualFriendsQuery(user_id_1=current_user_id, user_id_2=user_id)
    mutual_friends = await mediator.handle_query(query)

    return ApiResponse[MutualFriendsResponseSchema](
        data=MutualFriendsResponseSchema(mutual_friends=mutual_friends),
    )
