from unittest.mock import Mock

import pytest

from patterns_book.adapters.repository import AbstractRepository
from patterns_book.domain import model
from patterns_book.service import services
from tests.conftest import generate_sku, make_batch, make_order_line


class FakeRepository(AbstractRepository[model.Batch]):
    def __init__(self, batches: list[model.Batch]) -> None:
        self._batches = set(batches)

    def add(self, batch: model.Batch) -> None:
        self._batches.add(batch)

    def get(self, reference: str) -> model.Batch | None:
        return next((b for b in self._batches if b.reference == reference), None)

    def list(self) -> list[model.Batch]:
        return list(self._batches)


@pytest.fixture
def session() -> Mock:
    return Mock()


def test_allocate_returns_allocation(session: Mock) -> None:
    sku = generate_sku()
    line = make_order_line(sku, 10)
    batch = make_batch(sku, 100, eta=None)
    repo = FakeRepository([batch])

    result = services.allocate(line, repo, session)
    assert result == batch.reference
    session.commit.assert_called_once()


def test_allocate_raises_error_for_invalid_sku(session: Mock) -> None:
    sku = generate_sku()
    line = make_order_line("NONEXISTENTSKU", 10)
    batch = make_batch(sku, 100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(services.InvalidSkuError, match="Invalid sku NONEXISTENTSKU"):
        services.allocate(line, repo, session)


def test_allocate_raises_error_if_out_of_stock(session: Mock) -> None:
    sku = generate_sku()
    line = make_order_line(sku, 10)
    batch = make_batch(sku, 5)
    repo = FakeRepository([batch])

    with pytest.raises(model.OutOfStockError):
        services.allocate(line, repo, session)
