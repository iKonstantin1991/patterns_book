import abc

from sqlalchemy.orm import Session

from patterns_book.adapters.repository import AbstractRepository, ProductSQLRepository
from patterns_book.adapters.sessions import get_session
from patterns_book.domain import model as domain_model
from patterns_book.service.message_bus import AbstractMessageBus, InMemoryMessageBus


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
        message_bus: AbstractMessageBus,
    ) -> None:
        self.products = products
        self._session = session
        self._message_bus = message_bus

    def commit(self) -> None:
        self._session.commit()
        self._publish_events()

    def rollback(self) -> None:
        self._session.rollback()

    def _publish_events(self) -> None:
        for product in self.products.seen:
            while product.events:
                event = product.events.pop(0)
                self._message_bus.handle(event)


def create_sql_alchemy_uow() -> SqlAlchemyUnitOfWork:
    session = get_session()
    return SqlAlchemyUnitOfWork(
        products=ProductSQLRepository(session),
        session=session,
        message_bus=InMemoryMessageBus(),
    )
