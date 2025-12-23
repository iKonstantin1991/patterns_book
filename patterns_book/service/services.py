from __future__ import annotations

from typing import TYPE_CHECKING

from patterns_book.domain import model

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.orm import Session

    from patterns_book.adapters.repository import AbstractRepository
    from patterns_book.domain.model import Batch, OrderLine


class InvalidSkuError(Exception):
    pass


def allocate(line: OrderLine, repo: AbstractRepository[Batch], session: Session) -> str:
    batches = repo.list()
    if not _is_valid_sku(line.sku, batches):
        msg = f"Invalid sku {line.sku}"
        raise InvalidSkuError(msg)
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref


def _is_valid_sku(sku: str, batches: Sequence[Batch]) -> bool:
    return sku in {b.sku for b in batches}
