from typing import Any

from flask import Flask, request
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from patterns_book.adapters import db_tables, repository
from patterns_book.domain import model as domain_model
from patterns_book.service import models, services
from patterns_book.settings import get_settings

settings = get_settings()

db_tables.start_mappings()
get_session = sessionmaker(bind=create_engine(settings.postgres_dsn))
app = Flask(__name__)


@app.route("/allocation", methods=["POST"])
def allocate() -> tuple[dict[str, Any], int]:
    session = get_session()
    repo = repository.BatchSQLRepository(session)
    try:
        line = models.OrderLine.model_validate(request.json)
    except ValidationError as e:
        return {"errors": e.errors()}, 400

    try:
        batchref = services.allocate(line, repo, session)
    except (domain_model.OutOfStockError, services.InvalidSkuError) as e:
        return {"errors": [str(e)]}, 400

    return {"batchref": batchref}, 201
