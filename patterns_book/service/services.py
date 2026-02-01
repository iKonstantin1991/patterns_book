from __future__ import annotations

from typing import TYPE_CHECKING

from patterns_book.domain import model as domain_models

if TYPE_CHECKING:
    from collections.abc import Sequence

    from patterns_book.adapters.unit_of_work import AbstractUnitOfWork
    from patterns_book.service.models import Batch, OrderLine


class InvalidSkuError(Exception):
    pass


def add_batch(batch: Batch, uow: AbstractUnitOfWork) -> None:
    with uow:
        uow.batches.add(domain_models.Batch(batch.reference, batch.sku, batch.qty, batch.eta))
        uow.commit()


def allocate(line: OrderLine, uow: AbstractUnitOfWork) -> str:
    with uow:
        batches = uow.batches.list()
        if not _is_valid_sku(line.sku, batches):
            msg = f"Invalid sku {line.sku}"
            raise InvalidSkuError(msg)
        batch_reference = domain_models.allocate(domain_models.OrderLine(line.orderid, line.sku, line.qty), batches)
        uow.commit()
        return batch_reference


def _is_valid_sku(sku: str, batches: Sequence[domain_models.Batch]) -> bool:
    return sku in {b.sku for b in batches}
