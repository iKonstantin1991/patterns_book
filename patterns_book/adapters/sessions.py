from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

session_maker: sessionmaker[Session] | None = None


class SessionInitializationError(Exception):
    pass


@lru_cache
def init_sessionmaker(postgres_dsn: str) -> None:
    global session_maker  # noqa: PLW0603
    session_maker = sessionmaker(bind=create_engine(postgres_dsn))


def get_session() -> Session:
    if session_maker is None:
        msg = "session maker has not been initialized"
        raise SessionInitializationError(msg)
    return session_maker()
