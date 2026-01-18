import uuid
from datetime import date
from unittest.mock import Mock

import pytest

from patterns_book.adapters.repository import AbstractRepository
from patterns_book.domain import model as domain_model
from patterns_book.service import models, services
from tests.conftest import generate_sku


class FakeRepository(AbstractRepository[domain_model.Batch]):
    def __init__(self, batches: list[domain_model.Batch]) -> None:
        self._batches = set(batches)

    def add(self, batch: domain_model.Batch) -> None:
        self._batches.add(batch)

    def get(self, reference: str) -> domain_model.Batch | None:
        return next((b for b in self._batches if b.reference == reference), None)

    def list(self) -> list[domain_model.Batch]:
        return list(self._batches)


@pytest.fixture
def session() -> Mock:
    return Mock()


def make_batch(sku: str, qty: int, eta: date | None = None) -> models.Batch:
    return models.Batch(
        reference=str(uuid.uuid4()),
        sku=sku,
        qty=qty,
        eta=eta,
    )


def make_order_line(sku: str, qty: int) -> models.OrderLine:
    return models.OrderLine(
        orderid=str(uuid.uuid4()),
        sku=sku,
        qty=qty,
    )


def test_allocate_returns_allocation(session: Mock) -> None:
    sku = generate_sku()
    line = make_order_line(sku, 10)
    batch = make_batch(sku, 100, eta=None)
    repo = FakeRepository([domain_model.Batch(batch.reference, batch.sku, batch.qty, batch.eta)])

    result = services.allocate(line, repo, session)
    assert result == batch.reference
    session.commit.assert_called_once()


def test_allocate_raises_error_for_invalid_sku(session: Mock) -> None:
    sku = generate_sku()
    line = make_order_line("NONEXISTENTSKU", 10)
    batch = make_batch(sku, 100, eta=None)
    repo = FakeRepository([domain_model.Batch(batch.reference, batch.sku, batch.qty, batch.eta)])

    with pytest.raises(services.InvalidSkuError, match="Invalid sku NONEXISTENTSKU"):
        services.allocate(line, repo, session)


def test_allocate_raises_error_if_out_of_stock(session: Mock) -> None:
    sku = generate_sku()
    line = make_order_line(sku, 10)
    batch = make_batch(sku, 5)
    repo = FakeRepository([domain_model.Batch(batch.reference, batch.sku, batch.qty, batch.eta)])

    with pytest.raises(domain_model.OutOfStockError):
        services.allocate(line, repo, session)


def test_add_batch(session: Mock) -> None:
    batch = make_batch(generate_sku(), 10)
    repo = FakeRepository([])

    services.add_batch(batch, repo, session)

    assert repo.get(batch.reference) == domain_model.Batch(batch.reference, batch.sku, batch.qty, batch.eta)
    session.commit.assert_called_once()
