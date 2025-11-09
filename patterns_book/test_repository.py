from datetime import date
from typing import Generator

import pytest
from sqlalchemy.orm import Session, clear_mappers
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from patterns_book.repository import BatchSQLRepository
from patterns_book.db_tables import start_mappings

from patterns_book.conftest import generate_sku, make_batch, make_order_line


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
    session.execute(text("DELETE FROM allocations"))
    session.execute(text("DELETE FROM batches"))
    session.execute(text("DELETE FROM order_lines"))
    session.commit()


@pytest.fixture(scope="module", autouse=True)
def mapping() -> Generator[None, None, None]:
    start_mappings()
    yield
    clear_mappers()


def test_add_new_batch(session: Session) -> None:
    rep = BatchSQLRepository(session)
    batch = make_batch(generate_sku(), 10, date(1980, 1, 1))

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
    batch = make_batch(generate_sku(), 10, date(1980, 1, 1))

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


def test_create_batch_with_pre_allocated_order_line(session: Session) -> None:
    sku = generate_sku()
    batch = make_batch(sku, 10, date(2021, 1, 1))
    order_line = make_order_line(sku, 2)

    batch.allocate(order_line)

    rep = BatchSQLRepository(session)
    rep.add(batch)
    session.commit()

    retrieved_batch = rep.get(batch.reference)
    assert retrieved_batch is not None
    assert len(retrieved_batch._allocations) == 1
    assert order_line in retrieved_batch._allocations


def test_allocate_order_line_to_retrieved_batch(session: Session) -> None:
    sku = generate_sku()
    batch = make_batch(sku, 10, date(2021, 1, 1))

    rep = BatchSQLRepository(session)
    rep.add(batch)
    session.commit()

    retrieved_batch = rep.get(batch.reference)
    assert retrieved_batch is not None
    assert len(retrieved_batch._allocations) == 0

    order_line = make_order_line(sku, 2)
    retrieved_batch.allocate(order_line)

    session.commit()

    final_batch = rep.get(batch.reference)
    assert final_batch is not None
    assert len(final_batch._allocations) == 1
    assert order_line in final_batch._allocations


def test_deallocate_order_line_from_batch(session: Session) -> None:
    sku = generate_sku()
    batch = make_batch(sku, 10, date(2021, 1, 1))
    order_line = make_order_line(sku, 2)
    batch.allocate(order_line)

    rep = BatchSQLRepository(session)
    rep.add(batch)
    session.commit()

    retrieved_batch = rep.get(batch.reference)
    assert retrieved_batch is not None
    assert len(retrieved_batch._allocations) == 1
    assert order_line in retrieved_batch._allocations

    retrieved_batch.deallocate(order_line)
    session.commit()

    final_batch = rep.get(batch.reference)
    assert final_batch is not None
    assert len(final_batch._allocations) == 0


def test_get_batch_returns_none(session: Session) -> None:
    rep = BatchSQLRepository(session)
    assert rep.get("anything") is None
