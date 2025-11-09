import uuid
from datetime import date
from patterns_book.model import Batch, OrderLine


def generate_sku() -> str:
    return str(uuid.uuid4())


def make_batch(sku: str, qty: int, eta: date | None = None) -> Batch:
    return Batch(str(uuid.uuid4()), sku, qty, eta)


def make_order_line(sku: str, qty: int) -> OrderLine:
    return OrderLine(str(uuid.uuid4()), sku, qty)
