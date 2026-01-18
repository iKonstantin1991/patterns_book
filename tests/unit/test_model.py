from datetime import UTC, datetime, timedelta

import pytest

from patterns_book.domain.model import Batch, OrderLine, OutOfStockError, allocate
from tests.conftest import generate_sku, make_domain_batch, make_domain_order_line


def test_allocating_to_a_batch_reduces_the_available_quantity() -> None:
    batch, line = _make_batch_and_line(20, 2)

    batch.allocate(line)

    assert batch.available_quantity == 18


def test_allocating_sane_line_not_reduces_the_available_quantity() -> None:
    batch, line = _make_batch_and_line(20, 2)

    batch.allocate(line)
    batch.allocate(line)

    assert batch.available_quantity == 18


def test_deallocate_reduces_the_allocated_quantity() -> None:
    batch, line = _make_batch_and_line(20, 2)

    batch.allocate(line)
    batch.deallocate(line)

    assert batch.available_quantity == 20


def test_deallocate_if_line_is_not_allocated_does_not_reduces_the_available_quantity() -> None:
    batch, line = _make_batch_and_line(20, 2)

    batch.deallocate(line)

    assert batch.available_quantity == 20


def test_can_allocate_if_available_greater_than_required() -> None:
    batch, line = _make_batch_and_line(20, 2)

    assert batch.can_allocate(line)


def test_cannot_allocate_if_available_smaller_than_required() -> None:
    batch, line = _make_batch_and_line(2, 20)

    assert not batch.can_allocate(line)


def test_can_allocate_if_available_equal_to_required() -> None:
    batch, line = _make_batch_and_line(2, 2)

    assert batch.can_allocate(line)


def test_cannot_allocate_already_allocated() -> None:
    batch, line = _make_batch_and_line(20, 2)

    batch.allocate(line)
    assert not batch.can_allocate(line)


def test_cannot_allocate_different_sku() -> None:
    batch = make_domain_batch(generate_sku(), 20)
    line = make_domain_order_line(generate_sku(), 2)

    assert not batch.can_allocate(line)


def test_prefers_current_stock_batches_to_shipments() -> None:
    sku = generate_sku()
    in_stock_batch = make_domain_batch(sku, 100, eta=None)
    shipment_batch = make_domain_batch(sku, 100, eta=datetime.now(tz=UTC).date() + timedelta(days=1))
    line = make_domain_order_line(sku, 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches() -> None:
    today = datetime.now(tz=UTC).date()
    sku = generate_sku()
    earliest = make_domain_batch(sku, 100, eta=today)
    medium = make_domain_batch(sku, 100, eta=today + timedelta(days=5))
    latest = make_domain_batch(sku, 100, eta=today + timedelta(days=10))
    line = make_domain_order_line(sku, 10)

    allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref() -> None:
    sku = generate_sku()
    in_stock_batch = make_domain_batch(sku, 100, eta=None)
    shipment_batch = make_domain_batch(sku, 100, eta=datetime.now(tz=UTC).date() + timedelta(days=1))
    line = make_domain_order_line(sku, 10)

    allocation = allocate(line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_if_cannot_allocate() -> None:
    sku = generate_sku()
    batch = make_domain_batch(sku, 5)
    line = make_domain_order_line(sku, 10)

    with pytest.raises(OutOfStockError, match=sku):
        assert allocate(line, [batch]) is None


def test_allocate_later_if_earlier_cannot_allocate() -> None:
    sku = generate_sku()
    earlier = make_domain_batch(sku, 5, eta=datetime.now(tz=UTC).date())
    later = make_domain_batch(sku, 10, eta=datetime.now(tz=UTC).date() + timedelta(days=5))
    line = make_domain_order_line(sku, 7)

    allocation = allocate(line, [later, earlier])

    assert allocation == later.reference


def _make_batch_and_line(batch_qty: int, line_qty: int) -> tuple[Batch, OrderLine]:
    sku = generate_sku()
    batch = make_domain_batch(sku, batch_qty)
    line = make_domain_order_line(sku, line_qty)
    return batch, line
