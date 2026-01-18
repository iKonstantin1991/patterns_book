import uuid
from datetime import date

import pytest

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


def generate_sku() -> str:
    return str(uuid.uuid4())


def make_domain_batch(sku: str, qty: int, eta: date | None = None) -> domain_model.Batch:
    return domain_model.Batch(str(uuid.uuid4()), sku, qty, eta)


def make_domain_order_line(sku: str, qty: int) -> domain_model.OrderLine:
    return domain_model.OrderLine(str(uuid.uuid4()), sku, qty)
