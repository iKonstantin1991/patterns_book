from typing import Any

from flask import Blueprint, request
from pydantic import ValidationError

from patterns_book.adapters import unit_of_work
from patterns_book.domain import model as domain_model
from patterns_book.service import models, services

base_blueprint = Blueprint("api_v1", __name__, url_prefix="/api/v1")


@base_blueprint.route("/batches", methods=["POST"])
def add_batch() -> tuple[dict[str, Any], int]:
    try:
        batch = models.Batch.model_validate(request.json)
    except ValidationError as e:
        return {"errors": e.errors()}, 400

    uow = unit_of_work.create_sql_alchemy_uow()
    services.add_batch(batch, uow)
    return {}, 201


@base_blueprint.route("/allocation", methods=["POST"])
def allocate() -> tuple[dict[str, Any], int]:
    try:
        line = models.OrderLine.model_validate(request.json)
    except ValidationError as e:
        return {"errors": e.errors()}, 400

    uow = unit_of_work.create_sql_alchemy_uow()
    try:
        batchref = services.allocate(line, uow)
    except (domain_model.OutOfStockError, services.InvalidSkuError) as e:
        return {"errors": [str(e)]}, 400

    return {"batchref": batchref}, 201
