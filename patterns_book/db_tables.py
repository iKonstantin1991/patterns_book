from sqlalchemy import Table, MetaData, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import registry, relationship

from patterns_book.model import Batch, OrderLine

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
    Column("sku", String(255)),
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
