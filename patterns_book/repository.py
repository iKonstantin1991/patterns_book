import abc
from typing import Generic, TypeVar

from patterns_book import model
from sqlalchemy.orm import Session

T = TypeVar("T")


class AbstractRepository(abc.ABC, Generic[T]):
    @abc.abstractmethod
    def add(self, entity: T) -> None: ...

    @abc.abstractmethod
    def get(self, id_: str) -> T | None: ...


class SQLRepository(AbstractRepository[T]):
    def __init__(self, session: Session):
        self._session = session


class BatchSQLRepository(SQLRepository[model.Batch]):
    def add(self, entity: model.Batch) -> None:
        self._session.add(entity)

    def get(self, id_: str) -> model.Batch | None:
        return self._session.get(model.Batch, id_)
