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


def test_allocate_returns_none_if_out_of_stock(uow: "FakeUOF") -> None:
    sku = generate_sku()
    line = make_order_line(sku, 10)
    batch = make_batch(sku, 5)
    services.add_batch(batch, uow)

    actual = services.allocate(line, uow)

    assert actual is None


def test_add_batch(uow: "FakeUOF") -> None:
    batch = make_batch(generate_sku(), 10)

    services.add_batch(batch, uow)

    product = uow.products.get(batch.sku)
    assert product is not None
    assert domain_model.Batch(batch.reference, batch.sku, batch.qty, batch.eta) in product.batches
    assert uow.committed


class FakeRepository(AbstractRepository[domain_model.Product]):
    def __init__(self, products: list[domain_model.Product]) -> None:
        self._products = set(products)

    def add(self, batch: domain_model.Product) -> None:
        self._products.add(batch)

    def get(self, sku: str) -> domain_model.Product | None:
        return next((b for b in self._products if b.sku == sku), None)

    def list(self) -> list[domain_model.Product]:
        return list(self._products)


class FakeUOF(AbstractUnitOfWork):
    def __init__(
        self,
        products: AbstractRepository[domain_model.Product],
    ) -> None:
        self.products = products
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
