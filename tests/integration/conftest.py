from collections.abc import Generator

import pytest
from sqlalchemy.orm import clear_mappers

from patterns_book.adapters.db_tables import start_mappings


@pytest.fixture(scope="module", autouse=True)
def mapping() -> Generator[None, None, None]:
    start_mappings()
    yield
    clear_mappers()
