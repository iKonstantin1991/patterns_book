from datetime import date
from uuid import uuid4
from typing import Generator

import pytest
from sqlalchemy.orm import Session, clear_mappers
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from patterns_book.repository import BatchSQLRepository
from patterns_book.model import Batch
from patterns_book.db_tables import start_mappings


@pytest.fixture(scope="module")
def engine() -> Generator[Engine, None, None]:
    yield create_engine("postgresql://postgres:qwerty12345@localhost:5432/postgres")


@pytest.fixture
def session(engine: Engine) -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@pytest.fixture(autouse=True)
def cleanup(session: Session) -> Generator[None, None, None]:
    yield
    session.execute(text("DELETE FROM batches"))
    session.commit()


@pytest.fixture(scope="module", autouse=True)
def mapping() -> Generator[None, None, None]:
    start_mappings()
    yield
    clear_mappers()


def test_add_new_batch(session: Session) -> None:
    rep = BatchSQLRepository(session)
    batch = _make_batch(_generate_sku(), 10, date(1980, 1, 1))

    rep.add(batch)
    session.commit()

    actual = session.execute(
        text("""
            SELECT reference, sku, eta, purchased_quantity FROM batches
            WHERE reference = :reference
        """),
        {"reference": batch.reference},
    ).fetchone()
    assert actual == (batch.reference, batch.sku, batch.eta, batch._purchased_quantity)


def test_get_batch(session: Session) -> None:
    rep = BatchSQLRepository(session)
    batch = _make_batch(_generate_sku(), 10, date(1980, 1, 1))

    session.execute(
        text("""
            INSERT INTO batches (reference, sku, eta, purchased_quantity)
            VALUES (:reference, :sku, :eta, :purchased_quantity)
        """),
        {
            "reference": batch.reference,
            "sku": batch.sku,
            "eta": batch.eta,
            "purchased_quantity": batch._purchased_quantity,
        },
    )
    session.commit()

    actual = rep.get(batch.reference)
    assert actual == batch
    assert actual.sku == batch.sku
    assert actual.eta == batch.eta
    assert actual._purchased_quantity == batch._purchased_quantity


def test_get_batch_returns_none(session: Session) -> None:
    rep = BatchSQLRepository(session)
    assert rep.get("anything") is None


def _generate_sku() -> str:
    return str(uuid4())


def _make_batch(sku: str, qty: int, eta: date | None = None) -> Batch:
    return Batch(str(uuid4()), sku, qty, eta)
