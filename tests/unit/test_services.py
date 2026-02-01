import uuid
from datetime import date

import pytest

from patterns_book.adapters.repository import AbstractRepository
from patterns_book.adapters.unit_of_work import AbstractUnitOfWork
from patterns_book.domain import model as domain_model
from patterns_book.service import models, services
from tests.conftest import generate_sku


@pytest.fixture
def uow() -> "FakeUOF":
    return FakeUOF(FakeRepository([]))


def test_allocate_returns_allocation(uow: "FakeUOF") -> None:
    sku = generate_sku()
    line = make_order_line(sku, 10)
    batch = make_batch(sku, 100, eta=None)
    services.add_batch(batch, uow)

    result = services.allocate(line, uow)
    assert result == batch.reference
    assert uow.committed


def test_allocate_raises_error_for_invalid_sku(uow: "FakeUOF") -> None:
    sku = generate_sku()
    line = make_order_line("NONEXISTENTSKU", 10)
    batch = make_batch(sku, 100, eta=None)
    services.add_batch(batch, uow)

    with pytest.raises(services.InvalidSkuError, match="Invalid sku NONEXISTENTSKU"):
        services.allocate(line, uow)


def test_allocate_raises_error_if_out_of_stock(uow: "FakeUOF") -> None:
    sku = generate_sku()
    line = make_order_line(sku, 10)
    batch = make_batch(sku, 5)
    services.add_batch(batch, uow)

    with pytest.raises(domain_model.OutOfStockError):
        services.allocate(line, uow)


def test_add_batch(uow: "FakeUOF") -> None:
    batch = make_batch(generate_sku(), 10)

    services.add_batch(batch, uow)

    assert uow.batches.get(batch.reference) == domain_model.Batch(batch.reference, batch.sku, batch.qty, batch.eta)
    assert uow.committed


class FakeRepository(AbstractRepository[domain_model.Batch]):
    def __init__(self, batches: list[domain_model.Batch]) -> None:
        self._batches = set(batches)

    def add(self, batch: domain_model.Batch) -> None:
        self._batches.add(batch)

    def get(self, reference: str) -> domain_model.Batch | None:
        return next((b for b in self._batches if b.reference == reference), None)

    def list(self) -> list[domain_model.Batch]:
        return list(self._batches)


class FakeUOF(AbstractUnitOfWork):
    def __init__(
        self,
        batches: AbstractRepository[domain_model.Batch],
    ) -> None:
        self.batches = batches
        self.committed = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass


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
