from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    postgres_db: str

    @property
    def postgres_dsn(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
