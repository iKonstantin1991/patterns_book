from sqlalchemy import create_engine

from patterns_book.adapters.db_tables import metadata


def init_db():
    engine = create_engine(
        "postgresql://postgres:qwerty12345@localhost:5432/postgres",
        connect_args={"options": "-csearch_path=patterns"},
    )
    metadata.create_all(engine)


if __name__ == "__main__":
    init_db()
