from sqlalchemy import create_engine

from patterns_book.db_tables import metadata


def init_db():
    engine = create_engine("postgresql://postgres:qwerty12345@localhost:5432/postgres")
    metadata.create_all(engine)


if __name__ == "__main__":
    init_db()
