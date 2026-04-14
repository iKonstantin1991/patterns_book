from sqlalchemy import Column, Date, ForeignKey, Integer, MetaData, String, Table, event
from sqlalchemy.orm import registry, relationship

from patterns_book.domain.model import Batch, OrderLine, Product

metadata = MetaData()

order_lines = Table(
    "order_lines",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("qty", Integer),
    Column("orderid", String(255)),
)

batches = Table(
    "batches",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255)),
    Column("sku", ForeignKey("products.sku")),
    Column("purchased_quantity", Integer),
    Column("eta", Date, nullable=True),
)

allocations = Table(
    "allocations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", ForeignKey("order_lines.id")),
    Column("batch_id", ForeignKey("batches.id")),
)

products = Table(
    "products",
    metadata,
    Column("sku", String(255), primary_key=True),
    Column("version_number", Integer, nullable=False, server_default="0"),
)

mapper_registry = registry()


def start_mappings() -> None:
    mapper_registry.map_imperatively(
        Batch,
        batches,
        properties={
            "_purchased_quantity": batches.c.purchased_quantity,
            "_allocations": relationship(
                OrderLine,
                secondary=allocations,
                collection_class=set,
            ),
        },
    )
    mapper_registry.map_imperatively(OrderLine, order_lines)
    mapper_registry.map_imperatively(
        Product,
        products,
        properties={
            "_version_number": products.c.version_number,
            "batches": relationship(Batch, collection_class=list),
        },
    )


@event.listens_for(Product, "load")
def receive_load(product: Product, _: object) -> None:
    product.events = []
