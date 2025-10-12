from datetime import date, timedelta
import pytest
from uuid import uuid4

from model import allocate, Batch, OrderLine, OutOfStock


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch, line = _make_batch_and_line(20, 2)

    batch.allocate(line)

    assert batch.available_quantity == 18

def test_allocating_sane_line_not_reduces_the_available_quantity():
    batch, line = _make_batch_and_line(20, 2)

    batch.allocate(line)
    batch.allocate(line)

    assert batch.available_quantity == 18

def test_deallocate_reduces_the_allocated_quantity():
    batch, line = _make_batch_and_line(20, 2)

    batch.allocate(line)
    batch.deallocate(line)

    assert batch.available_quantity == 20

def test_deallocate_if_line_is_not_allocated_does_not_reduces_the_available_quantity():
    batch, line = _make_batch_and_line(20, 2)

    batch.deallocate(line)

    assert batch.available_quantity == 20

def test_can_allocate_if_available_greater_than_required():
    batch, line = _make_batch_and_line(20, 2)

    assert batch.can_allocate(line)

def test_cannot_allocate_if_available_smaller_than_required():
    batch, line = _make_batch_and_line(2, 20)

    assert not batch.can_allocate(line)


def test_can_allocate_if_available_equal_to_required():
    batch, line = _make_batch_and_line(2, 2)

    assert batch.can_allocate(line)

def test_cannot_allocate_already_allocated():
    batch, line = _make_batch_and_line(20, 2)

    batch.allocate(line)
    assert not batch.can_allocate(line)

def test_cannot_allocate_different_sku():
    batch = _make_batch(_generate_sku(), 20)
    line = _make_order_line(_generate_sku(), 2)

    assert not batch.can_allocate(line)

def test_prefers_current_stock_batches_to_shipments():
    sku = _generate_sku()
    in_stock_batch = _make_batch(sku, 100, eta=None)
    shipment_batch = _make_batch(sku, 100, eta=date.today() + timedelta(days=1))
    line = _make_order_line(sku, 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100

def test_prefers_earlier_batches():
    today = date.today()
    sku = _generate_sku()
    earliest = _make_batch(sku, 100, eta=today)
    medium = _make_batch(sku, 100, eta=today + timedelta(days=5))
    latest = _make_batch(sku, 100, eta=today + timedelta(days=10))
    line = _make_order_line(sku, 10)

    allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100

def test_returns_allocated_batch_ref():
    sku = _generate_sku()
    in_stock_batch = _make_batch(sku, 100, eta=None)
    shipment_batch = _make_batch(sku, 100, eta=date.today() + timedelta(days=1))
    line = _make_order_line(sku, 10)

    allocation = allocate(line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.reference

def test_raises_out_of_stock_if_cannot_allocate():
    sku = _generate_sku()
    batch = _make_batch(sku, 5)
    line = _make_order_line(sku, 10)

    with pytest.raises(OutOfStock, match=sku):
        allocate(line, [batch]) is None

def test_allocate_later_if_earlier_cannot_allocate():
    sku = _generate_sku()
    earlier = _make_batch(sku, 5, eta=date.today())
    later = _make_batch(sku, 10, eta=date.today() + timedelta(days=5))
    line = _make_order_line(sku, 7)

    allocation = allocate(line, [later, earlier])

    assert allocation == later.reference

def _generate_sku() -> str:
    return str(uuid4())

def _make_batch(sku: str, qty: int, eta: date | None = None) -> Batch:
    return Batch(str(uuid4()), sku, qty, eta)

def _make_order_line(sku: str, qty: int) -> OrderLine:
    return OrderLine(str(uuid4()), sku, qty)

def _make_batch_and_line(batch_qty: int, line_qty: int) -> tuple[Batch, OrderLine]:
    sku = _generate_sku()
    batch = _make_batch(sku, batch_qty)
    line = _make_order_line(sku, line_qty)
    return batch, line
