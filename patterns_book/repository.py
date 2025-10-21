import abc
from typing import Generic, TypeVar

from patterns_book import model

T = TypeVar("T")


class AbstractRepository(abc.ABC, Generic[T]):
    @abc.abstractmethod
    def add(self, batch: T) -> None: ...

    @abc.abstractmethod
    def get(self, id_: str) -> T | None: ...
