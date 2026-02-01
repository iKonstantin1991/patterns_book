from unittest.mock import Mock

import pytest

from patterns_book.adapters.unit_of_work import SqlAlchemyUnitOfWork


@pytest.fixture
def session() -> Mock:
    return Mock(spec=["commit", "rollback"])


@pytest.fixture
def batches() -> Mock:
    return Mock()


def test_sqlalchemy_uow_commit(session: Mock, batches: Mock) -> None:
    uow = SqlAlchemyUnitOfWork(batches, session)
    uow.commit()

    session.commit.assert_called_once()


def test_sqlalchemy_uow_rollback(session: Mock, batches: Mock) -> None:
    uow = SqlAlchemyUnitOfWork(batches, session)
    uow.rollback()

    session.rollback.assert_called_once()


def test_sqlalchemy_uow_context_manager_rollback(session: Mock, batches: Mock) -> None:
    uow = SqlAlchemyUnitOfWork(batches, session)

    with uow:
        pass

    session.rollback.assert_called_once()
    session.commit.assert_not_called()
