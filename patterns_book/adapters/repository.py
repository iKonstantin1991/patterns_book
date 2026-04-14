import abc
from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from patterns_book.domain import model

T = TypeVar("T")


class AbstractRepository(abc.ABC, Generic[T]):
    seen: set[T]

    @abc.abstractmethod
    def add(self, entity: T) -> None: ...

    @abc.abstractmethod
    def get(self, id_: str) -> T | None: ...

    @abc.abstractmethod
    def list(self) -> Sequence[T]: ...


class SQLRepository(AbstractRepository[T]):
    def __init__(self, session: Session) -> None:
        self._session = session


class ProductSQLRepository(SQLRepository[model.Product]):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.seen = set()

    def add(self, product: model.Product) -> None:
        self._session.add(product)
        self.seen.add(product)

    def get(self, sku: str) -> model.Product | None:
        product = self._session.execute(select(model.Product).filter_by(sku=sku)).scalars().first()
        if product:
            self.seen.add(product)
        return product

    def list(self) -> Sequence[model.Product]:
        products = self._session.execute(select(model.Product)).scalars().all()
        self.seen.update(products)
        return products
