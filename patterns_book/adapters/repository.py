import abc
from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from patterns_book.domain import model

T = TypeVar("T")


class AbstractRepository(abc.ABC, Generic[T]):
    @abc.abstractmethod
    def add(self, entity: T) -> None: ...

    @abc.abstractmethod
    def get(self, id_: str) -> T | None: ...

    @abc.abstractmethod
    def list(self) -> Sequence[T]: ...


class SQLRepository(AbstractRepository[T]):
    def __init__(self, session: Session) -> None:
        self._session = session


class BatchSQLRepository(SQLRepository[model.Batch]):
    def add(self, batch: model.Batch) -> None:
        self._session.add(batch)

    def get(self, reference: str) -> model.Batch | None:
        return self._session.execute(select(model.Batch).filter_by(reference=reference)).scalars().first()

    def list(self) -> Sequence[model.Batch]:
        return self._session.execute(select(model.Batch)).scalars().all()
