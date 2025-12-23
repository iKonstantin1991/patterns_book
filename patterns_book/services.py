from __future__ import annotations

from typing import Sequence

from sqlalchemy.orm import Session

from patterns_book import model
from patterns_book.model import OrderLine, Batch
from patterns_book.repository import AbstractRepository


class InvalidSku(Exception):
    pass


def allocate(line: OrderLine, repo: AbstractRepository[Batch], session: Session) -> str:
    batches = repo.list()
    if not _is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref


def _is_valid_sku(sku: str, batches: Sequence[Batch]) -> bool:
    return sku in {b.sku for b in batches}
