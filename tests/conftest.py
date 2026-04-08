import uuid
from collections.abc import Generator
from datetime import date

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker as sa_sessionmaker

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
        postgres_schema="patterns",
    )


@pytest.fixture(scope="session")
def engine(settings: Settings) -> Engine:
    return create_engine(
        settings.postgres_dsn,
        connect_args={"options": f"-csearch_path={settings.postgres_schema}"},
        isolation_level="REPEATABLE READ",
    )


@pytest.fixture(scope="session")
def sessionmaker(engine: Engine) -> sa_sessionmaker[Session]:
    return sa_sessionmaker(bind=engine)


@pytest.fixture
def session(sessionmaker: sa_sessionmaker[Session]) -> Session:
    return sessionmaker()


@pytest.fixture
def db_cleanup(session: Session) -> Generator[None, None, None]:
    yield
    session.execute(text("DELETE FROM allocations"))
    session.execute(text("DELETE FROM batches"))
    session.execute(text("DELETE FROM order_lines"))
    session.execute(text("DELETE FROM products"))
    session.commit()


def generate_sku() -> str:
    return str(uuid.uuid4())


def make_domain_batch(sku: str, qty: int, eta: date | None = None) -> domain_model.Batch:
    return domain_model.Batch(str(uuid.uuid4()), sku, qty, eta)


def make_domain_order_line(sku: str, qty: int) -> domain_model.OrderLine:
    return domain_model.OrderLine(str(uuid.uuid4()), sku, qty)


def make_domain_product(sku: str, batches: list[domain_model.Batch] | None = None) -> domain_model.Product:
    return domain_model.Product(sku, batches or [])
