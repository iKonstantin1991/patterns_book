from typing import Any

from flask import Blueprint, request
from pydantic import ValidationError

from patterns_book.adapters import repository
from patterns_book.adapters.sessions import get_session
from patterns_book.domain import model as domain_model
from patterns_book.service import models, services

base_blueprint = Blueprint("api_v1", __name__, url_prefix="/api/v1")


@base_blueprint.route("/batches", methods=["POST"])
def add_batch() -> tuple[dict[str, Any], int]:
    session = get_session()
    repo = repository.BatchSQLRepository(session)
    try:
        batch = models.Batch.model_validate(request.json)
    except ValidationError as e:
        return {"errors": e.errors()}, 400

    services.add_batch(batch, repo, session)
    return {}, 201


@base_blueprint.route("/allocation", methods=["POST"])
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
