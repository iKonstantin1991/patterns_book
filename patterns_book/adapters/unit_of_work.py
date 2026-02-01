import abc

from sqlalchemy.orm import Session

from patterns_book.adapters.repository import AbstractRepository, BatchSQLRepository
from patterns_book.adapters.sessions import get_session
from patterns_book.domain import model as domain_model


class AbstractUnitOfWork(abc.ABC):
    batches: AbstractRepository[domain_model.Batch]

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
        batches: AbstractRepository[domain_model.Batch],
        session: Session,
    ) -> None:
        self.batches = batches
        self._session = session

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()


def create_sql_alchemy_uow() -> SqlAlchemyUnitOfWork:
    session = get_session()
    return SqlAlchemyUnitOfWork(BatchSQLRepository(session), session)
