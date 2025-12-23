from typing import Any

from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from patterns_book.adapters import db_tables, repository
from patterns_book.domain import model
from patterns_book.service import services
from patterns_book.settings import get_settings

settings = get_settings()

db_tables.start_mappings()
get_session = sessionmaker(bind=create_engine(settings.postgres_dsn))
app = Flask(__name__)


@app.route("/allocation", methods=["POST"])
def allocate() -> tuple[dict[str, Any], int]:
    session = get_session()
    repo = repository.BatchSQLRepository(session)
    line = model.OrderLine(
        request.json["orderid"],
        request.json["sku"],
        request.json["qty"],
    )

    try:
        batchref = services.allocate(line, repo, session)
    except (model.OutOfStockError, services.InvalidSkuError) as e:
        return {"message": str(e)}, 400

    return {"batchref": batchref}, 201
