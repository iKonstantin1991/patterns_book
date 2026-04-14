from unittest.mock import Mock

import pytest

from patterns_book.adapters.unit_of_work import SqlAlchemyUnitOfWork
from patterns_book.domain.events import Event
from patterns_book.service.message_bus import AbstractMessageBus


@pytest.fixture
def session() -> Mock:
    return Mock(spec=["commit", "rollback"])


@pytest.fixture
def event() -> Mock:
    return Mock()


@pytest.fixture
def message_bus() -> "_FakeMessageBus":
    return _FakeMessageBus()


@pytest.fixture
def products(event: Mock) -> Mock:
    return Mock(seen=[Mock(events=[event])])


def test_sqlalchemy_uow_commit(
    session: Mock,
    products: Mock,
    message_bus: "_FakeMessageBus",
    event: Mock,
) -> None:
    uow = SqlAlchemyUnitOfWork(products, session, message_bus)
    uow.commit()

    session.commit.assert_called_once()
    assert message_bus.handled_events == [event]


def test_sqlalchemy_uow_rollback(session: Mock, products: Mock, message_bus: "_FakeMessageBus") -> None:
    uow = SqlAlchemyUnitOfWork(products, session, message_bus)
    uow.rollback()

    session.rollback.assert_called_once()
    assert message_bus.handled_events == []


def test_sqlalchemy_uow_context_manager_rollback(
    session: Mock,
    products: Mock,
    message_bus: "_FakeMessageBus",
) -> None:
    uow = SqlAlchemyUnitOfWork(products, session, message_bus)

    with uow:
        pass

    session.rollback.assert_called_once()
    session.commit.assert_not_called()


class _FakeMessageBus(AbstractMessageBus):
    def __init__(self) -> None:
        self.handled_events: list[Event] = []

    def handle(self, event: Event) -> None:
        self.handled_events.append(event)
