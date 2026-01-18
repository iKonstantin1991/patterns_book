from collections.abc import Generator

import pytest
from flask.testing import FlaskClient
from sqlalchemy.orm import clear_mappers

from patterns_book.main import create_app_with_settings
from patterns_book.settings import Settings
from tests.conftest import generate_sku

pytestmark = pytest.mark.usefixtures("db_cleanup")


@pytest.fixture(scope="module")
def test_client(settings: Settings) -> Generator[FlaskClient, None, None]:
    app = create_app_with_settings(settings)
    yield app.test_client()
    clear_mappers()


def test_successful_allocation(test_client: FlaskClient) -> None:
    early_batch, later_batch = "early_batch", "later_batch"
    sku = generate_sku()
    test_client.post(
        "/api/v1/batches",
        json={
            "reference": early_batch,
            "sku": sku,
            "qty": 100,
            "eta": "2011-01-01",
        },
    )

    test_client.post(
        "/api/v1/batches",
        json={
            "reference": later_batch,
            "sku": sku,
            "qty": 100,
            "eta": "2012-01-01",
        },
    )

    response = test_client.post(
        "/api/v1/allocation",
        json={
            "orderid": "order1",
            "sku": sku,
            "qty": 10,
        },
    )

    assert response.status_code == 201
    assert response.json is not None
    assert response.json.get("batchref") == early_batch
