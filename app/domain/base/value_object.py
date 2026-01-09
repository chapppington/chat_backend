from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import (
    Any,
    Generic,
    TypeVar,
)


ValueType = TypeVar("ValueType", bound=Any)


@dataclass(frozen=True)
class BaseValueObject(ABC, Generic[ValueType]):
    value: ValueType

    def __post_init__(self):
        self.validate()

    @abstractmethod
    def validate(self): ...

    @abstractmethod
    def as_generic_type(self) -> ValueType: ...
