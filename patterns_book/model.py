from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass(frozen=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int


class Batch:
    def __init__(
        self, ref: str, sku: str, qty: int, eta: date | None = None
    ) -> None:
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self.available_quantity = qty
        self._purchased_quantity = qty
        self._allocations: set[OrderLine] = set()

    def allocate(self, line: OrderLine) -> None:
        if self.can_allocate(line):
            self.available_quantity -= line.qty
            self._allocations.add(line)

    def deallocate(self, line: OrderLine) -> None:
        if line in self._allocations:
            self.available_quantity += line.qty
            self._allocations.remove(line)

    def can_allocate(self, line: OrderLine) -> bool:
        return (
            self.sku == line.sku
            and self.available_quantity >= line.qty
            and line not in self._allocations
        )

    def __gt__(self, other: Batch) -> bool:
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Batch):
            return False
        return self.reference == other.reference


class OutOfStock(Exception):
    pass


def allocate(line: OrderLine, batches: list[Batch]) -> str | None:
    try:
        batch = next((b for b in sorted(batches) if b.can_allocate(line)))
    except StopIteration:
        raise OutOfStock(f"Cannot allocate {line}")

    batch.allocate(line)
    return batch.reference
