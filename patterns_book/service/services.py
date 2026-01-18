from __future__ import annotations

from typing import TYPE_CHECKING

from patterns_book.domain import model as domain_models

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.orm import Session

    from patterns_book.adapters.repository import AbstractRepository
    from patterns_book.service.models import Batch, OrderLine


class InvalidSkuError(Exception):
    pass


def add_batch(batch: Batch, repo: AbstractRepository[domain_models.Batch], session: Session) -> None:
    repo.add(domain_models.Batch(batch.reference, batch.sku, batch.qty, batch.eta))
    session.commit()


def allocate(line: OrderLine, repo: AbstractRepository[domain_models.Batch], session: Session) -> str:
    batches = repo.list()
    if not _is_valid_sku(line.sku, batches):
        msg = f"Invalid sku {line.sku}"
        raise InvalidSkuError(msg)
    batchref = domain_models.allocate(domain_models.OrderLine(line.orderid, line.sku, line.qty), batches)
    session.commit()
    return batchref


def _is_valid_sku(sku: str, batches: Sequence[domain_models.Batch]) -> bool:
    return sku in {b.sku for b in batches}
