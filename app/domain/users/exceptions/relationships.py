from dataclasses import dataclass
from uuid import UUID

from domain.base.exceptions import DomainException


@dataclass(eq=False)
class RelationshipException(DomainException):
    @property
    def message(self) -> str:
        return "Relationship exception occurred"


@dataclass(eq=False)
class CannotAddSelfException(RelationshipException):
    user_id: UUID
    relationship_type: str

    @property
    def message(self) -> str:
        return f"Cannot add yourself as {self.relationship_type}"
