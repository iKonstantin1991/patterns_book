from flask import Flask

from patterns_book.adapters import db_tables
from patterns_book.adapters.sessions import init_sessionmaker
from patterns_book.endpoints.api import base_blueprint
from patterns_book.settings import Settings, get_settings


def create_app() -> Flask:
    settings = get_settings()
    return create_app_with_settings(settings)


def create_app_with_settings(settings: Settings) -> Flask:
    init_sessionmaker(settings.postgres_dsn)
    db_tables.start_mappings()

    app = Flask(__name__)
    app.register_blueprint(base_blueprint)

    return app
