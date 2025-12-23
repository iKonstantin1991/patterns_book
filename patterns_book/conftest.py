import uuid
from datetime import date

import pytest

from patterns_book.settings import Settings
from patterns_book.model import Batch, OrderLine


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings(
        postgres_user="postgres",
        postgres_password="qwerty12345",
        postgres_host="localhost",
        postgres_port=5432,
        postgres_db="postgres",
    )


def generate_sku() -> str:
    return str(uuid.uuid4())


def make_batch(sku: str, qty: int, eta: date | None = None) -> Batch:
    return Batch(str(uuid.uuid4()), sku, qty, eta)


def make_order_line(sku: str, qty: int) -> OrderLine:
    return OrderLine(str(uuid.uuid4()), sku, qty)
