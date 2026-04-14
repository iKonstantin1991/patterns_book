from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from patterns_book.domain import events

if TYPE_CHECKING:
    from datetime import date


@dataclass(unsafe_hash=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int


class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: date | None = None) -> None:
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations: set[OrderLine] = set()

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - sum(line.qty for line in self._allocations)

    def allocate(self, line: OrderLine) -> None:
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine) -> None:
        if line in self._allocations:
            self._allocations.remove(line)

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty and line not in self._allocations

    def __gt__(self, other: Batch) -> bool:
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Batch):
            return False
        return self.reference == other.reference

    def __hash__(self) -> int:
        return hash(self.reference)


class Product:
    def __init__(self, sku: str, batches: list[Batch], version_number: int = 0) -> None:
        self.sku = sku
        self.batches = batches
        self.events: list[events.Event] = []
        self._version_number = version_number

    def allocate(self, line: OrderLine) -> str | None:
        try:
            batch = next(b for b in sorted(self.batches) if b.can_allocate(line))
        except StopIteration:
            self.events.append(events.OutOfStock(self.sku))
            return None

        batch.allocate(line)
        self._version_number += 1
        return batch.reference

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Product):
            return False
        return self.sku == other.sku and self.batches == other.batches

    def __hash__(self) -> int:
        return hash(self.sku)
