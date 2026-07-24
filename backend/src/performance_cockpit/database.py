from collections.abc import Generator
from functools import lru_cache
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine, inspect
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from performance_cockpit.config import Settings, get_settings


@lru_cache
def get_engine() -> Engine:
    return create_database_engine(get_settings())


def create_database_engine(settings: Settings) -> Engine:
    connect_args = (
        {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
    )
    return create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)


def migration_config(settings: Settings, migrations_dir: Path) -> Config:
    config = Config()
    config.set_main_option("script_location", str(migrations_dir))
    config.set_main_option("sqlalchemy.url", settings.database_url)
    return config


def initialize_database(
    settings: Settings | None = None,
    migrations_dir: Path | None = None,
) -> None:
    """Create or migrate the schema, adopting databases created by Release 0.4."""
    resolved_settings = settings or get_settings()
    url = make_url(resolved_settings.database_url)
    if url.drivername.startswith("sqlite") and url.database and url.database != ":memory:":
        Path(url.database).parent.mkdir(parents=True, exist_ok=True)
    engine = create_database_engine(resolved_settings)
    try:
        database_tables = set(inspect(engine).get_table_names())
        resolved_migrations = (
            migrations_dir
            or resolved_settings.migrations_dir
            or Path(__file__).resolve().parents[2] / "migrations"
        )
        config = migration_config(resolved_settings, resolved_migrations)
        if "metric_definitions" in database_tables and "alembic_version" not in database_tables:
            command.stamp(config, "0001")
        command.upgrade(config, "head")
    finally:
        engine.dispose()


def clear_database_caches() -> None:
    get_session_factory.cache_clear()
    get_engine.cache_clear()


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    with get_session_factory()() as session:
        yield session
