import uuid
from collections.abc import Generator
from datetime import date

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from patterns_book.domain import model as domain_model
from patterns_book.settings import Settings


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings(
        postgres_user="postgres",
        postgres_password="qwerty12345",
        postgres_host="localhost",
        postgres_port=5432,
        postgres_db="postgres",
    )


@pytest.fixture(scope="module")
def engine(settings: Settings) -> Engine:
    return create_engine(settings.postgres_dsn)


@pytest.fixture
def session(engine: Engine) -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@pytest.fixture
def db_cleanup(session: Session) -> Generator[None, None, None]:
    yield
    session.execute(text("DELETE FROM allocations"))
    session.execute(text("DELETE FROM batches"))
    session.execute(text("DELETE FROM order_lines"))
    session.commit()


def generate_sku() -> str:
    return str(uuid.uuid4())


def make_domain_batch(sku: str, qty: int, eta: date | None = None) -> domain_model.Batch:
    return domain_model.Batch(str(uuid.uuid4()), sku, qty, eta)


def make_domain_order_line(sku: str, qty: int) -> domain_model.OrderLine:
    return domain_model.OrderLine(str(uuid.uuid4()), sku, qty)
