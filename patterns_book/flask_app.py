from typing import Any

from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from patterns_book.settings import get_settings
from patterns_book import model
from patterns_book import db_tables
from patterns_book import repository
from patterns_book import services

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
    except (model.OutOfStock, services.InvalidSku) as e:
        return {"message": str(e)}, 400

    return {"batchref": batchref}, 201
