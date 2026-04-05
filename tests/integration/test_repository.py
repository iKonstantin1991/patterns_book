from collections.abc import Generator
from datetime import date

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session, clear_mappers

from patterns_book.adapters.db_tables import start_mappings
from patterns_book.adapters.repository import ProductSQLRepository
from tests.conftest import generate_sku, make_domain_batch, make_domain_order_line, make_domain_product

pytestmark = pytest.mark.usefixtures("db_cleanup")


@pytest.fixture(scope="module", autouse=True)
def mapping() -> Generator[None, None, None]:
    start_mappings()
    yield
    clear_mappers()


def test_add_new_product(session: Session) -> None:
    sku = generate_sku()
    product = make_domain_product(sku)
    rep = ProductSQLRepository(session)

    rep.add(product)
    session.commit()

    actual = session.execute(
        text("SELECT sku FROM products WHERE sku = :sku"),
        {"sku": sku},
    ).fetchone()
    assert actual == (sku,)


def test_get_product(session: Session) -> None:
    rep = ProductSQLRepository(session)
    sku = generate_sku()
    product = make_domain_product(sku)

    session.execute(
        text("INSERT INTO products (sku) VALUES (:sku)"),
        {"sku": sku},
    )
    session.commit()

    actual = rep.get(sku)
    assert actual == product


def test_create_product_with_batch_and_pre_allocated_order_line(session: Session) -> None:
    sku = generate_sku()
    batch = make_domain_batch(sku, 10, date(2021, 1, 1))
    product = make_domain_product(sku, [batch])
    order_line = make_domain_order_line(sku, 2)

    product.allocate(order_line)

    rep = ProductSQLRepository(session)
    rep.add(product)
    session.commit()

    retrieved_product = rep.get(product.sku)
    assert retrieved_product is not None
    assert len(retrieved_product.batches) == 1
    assert len(retrieved_product.batches[0]._allocations) == 1
    assert order_line in retrieved_product.batches[0]._allocations


def test_add_batch_to_retrieved_product(session: Session) -> None:
    sku = generate_sku()
    product = make_domain_product(sku)

    rep = ProductSQLRepository(session)
    rep.add(product)
    session.commit()

    retrieved_product = rep.get(product.sku)
    assert retrieved_product is not None

    batch = make_domain_batch(sku, 10, date(2021, 1, 1))
    retrieved_product.batches.append(batch)
    session.commit()

    final_product = rep.get(product.sku)
    assert final_product is not None
    assert len(final_product.batches) == 1
    assert final_product.batches[0] == batch


def test_remove_batch_from_retrieved_product(session: Session) -> None:
    sku = generate_sku()
    batch = make_domain_batch(sku, 10, date(2021, 1, 1))
    product = make_domain_product(sku, [batch])

    rep = ProductSQLRepository(session)
    rep.add(product)
    session.commit()

    retrieved_product = rep.get(product.sku)
    assert retrieved_product is not None
    assert len(retrieved_product.batches) == 1

    retrieved_product.batches = []
    session.commit()

    final_product = rep.get(product.sku)
    assert final_product is not None
    assert len(final_product.batches) == 0


def test_allocate_order_line_to_retrieved_product(session: Session) -> None:
    sku = generate_sku()
    batch = make_domain_batch(sku, 10, date(2021, 1, 1))
    product = make_domain_product(sku, [batch])

    rep = ProductSQLRepository(session)
    rep.add(product)
    session.commit()

    retrieved_product = rep.get(product.sku)
    assert retrieved_product is not None

    order_line = make_domain_order_line(sku, 2)
    retrieved_product.allocate(order_line)

    session.commit()

    final_product = rep.get(product.sku)
    assert final_product is not None
    assert len(final_product.batches) == 1
    assert len(final_product.batches[0]._allocations) == 1
    assert order_line in final_product.batches[0]._allocations


def test_get_batch_returns_none(session: Session) -> None:
    rep = ProductSQLRepository(session)
    assert rep.get("anything") is None


def test_list_empty_repository(session: Session) -> None:
    rep = ProductSQLRepository(session)
    batches = rep.list()
    assert len(batches) == 0
    assert batches == []


def test_list_multiple_products(session: Session) -> None:
    rep = ProductSQLRepository(session)

    product1 = make_domain_product(generate_sku())
    product2 = make_domain_product(generate_sku())
    product3 = make_domain_product(generate_sku())

    rep.add(product1)
    rep.add(product2)
    rep.add(product3)
    session.commit()

    products = rep.list()
    assert len(products) == 3

    product_skus = {product.sku for product in products}
    assert product1.sku in product_skus
    assert product2.sku in product_skus
    assert product3.sku in product_skus
