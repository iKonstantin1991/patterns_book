from __future__ import annotations

from typing import TYPE_CHECKING

from patterns_book.domain import model as domain_models

if TYPE_CHECKING:
    from patterns_book.adapters.unit_of_work import AbstractUnitOfWork
    from patterns_book.service.models import Batch, OrderLine


class InvalidSkuError(Exception):
    pass


def add_batch(batch: Batch, uow: AbstractUnitOfWork) -> None:
    with uow:
        product = uow.products.get(batch.sku)
        if product is None:
            product = domain_models.Product(batch.sku, batches=[])
            uow.products.add(product)

        product.batches.append(domain_models.Batch(batch.reference, batch.sku, batch.qty, batch.eta))
        uow.commit()


def allocate(line: OrderLine, uow: AbstractUnitOfWork) -> str:
    with uow:
        product = uow.products.get(line.sku)
        if product is None:
            msg = f"Invalid sku {line.sku}"
            raise InvalidSkuError(msg)

        batch_reference = product.allocate(domain_models.OrderLine(line.orderid, line.sku, line.qty))
        uow.commit()
        return batch_reference
