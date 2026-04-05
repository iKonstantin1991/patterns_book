import abc

from sqlalchemy.orm import Session

from patterns_book.adapters.repository import AbstractRepository, ProductSQLRepository
from patterns_book.adapters.sessions import get_session
from patterns_book.domain import model as domain_model


class AbstractUnitOfWork(abc.ABC):
    products: AbstractRepository[domain_model.Product]

    def __enter__(self) -> "AbstractUnitOfWork":
        return self

    def __exit__(self, *_: object) -> None:
        self.rollback()

    @abc.abstractmethod
    def commit(self) -> None: ...

    @abc.abstractmethod
    def rollback(self) -> None: ...


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(
        self,
        products: AbstractRepository[domain_model.Product],
        session: Session,
    ) -> None:
        self.products = products
        self._session = session

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()


def create_sql_alchemy_uow() -> SqlAlchemyUnitOfWork:
    session = get_session()
    return SqlAlchemyUnitOfWork(ProductSQLRepository(session), session)
