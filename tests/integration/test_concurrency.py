import threading
import time
from collections.abc import Callable

import pytest
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker as sa_sessionmaker

from patterns_book.adapters.repository import ProductSQLRepository
from patterns_book.adapters.unit_of_work import SqlAlchemyUnitOfWork
from patterns_book.service.message_bus import InMemoryMessageBus
from tests.conftest import generate_sku, make_domain_batch, make_domain_order_line, make_domain_product

pytestmark = pytest.mark.usefixtures("db_cleanup")


@pytest.fixture
def batch_qty() -> int:
    return 100


@pytest.fixture
def order_line_qty() -> int:
    return 10


@pytest.fixture
def uow_factory(sessionmaker: sa_sessionmaker[Session]) -> Callable[[], SqlAlchemyUnitOfWork]:
    def factory() -> SqlAlchemyUnitOfWork:
        session = sessionmaker()
        return SqlAlchemyUnitOfWork(ProductSQLRepository(session), session, InMemoryMessageBus())

    return factory


@pytest.fixture
def product_sku(uow_factory: Callable[[], SqlAlchemyUnitOfWork], batch_qty: int) -> str:
    uow = uow_factory()
    with uow:
        sku = generate_sku()
        batch = make_domain_batch(sku, batch_qty)
        product = make_domain_product(sku, [batch])
        uow.products.add(product)
        uow.commit()
        return sku


def test_concurrent_allocations(
    product_sku: str, uow_factory: Callable[[], SqlAlchemyUnitOfWork], batch_qty: int, order_line_qty: int
) -> None:
    t1 = threading.Thread(target=_make_test_allocation, args=(product_sku, uow_factory, order_line_qty))
    t2 = threading.Thread(target=_make_test_allocation, args=(product_sku, uow_factory, order_line_qty))

    for t in (t1, t2):
        t.start()

    for t in (t1, t2):
        t.join()

    uow = uow_factory()
    product = uow.products.get(product_sku)
    assert product is not None
    expected_qty = batch_qty - order_line_qty
    assert len(product.batches) == 1
    assert product.batches[0].available_quantity == expected_qty


def _make_test_allocation(sku: str, uow_factory: Callable[[], SqlAlchemyUnitOfWork], order_line_qty: int) -> None:
    try:
        uow = uow_factory()
        with uow:
            product = uow.products.get(sku)
            if not product:
                return
            time.sleep(0.1)
            product.allocate(make_domain_order_line(sku, order_line_qty))
            uow.commit()
    except Exception:  # noqa: BLE001
        pass
