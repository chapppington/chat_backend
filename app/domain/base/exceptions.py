from dataclasses import dataclass


@dataclass(eq=False)
class ApplicationException(Exception):
    @property
    def message(self) -> str:
        return "Application exception occurred"


@dataclass(eq=False)
class DomainException(ApplicationException):
    @property
    def message(self) -> str:
        return "Domain exception occurred"
