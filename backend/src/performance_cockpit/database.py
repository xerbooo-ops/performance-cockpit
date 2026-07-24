from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from performance_cockpit.config import Settings, application_data_dir, get_settings
from performance_cockpit.models import Base


@lru_cache
def get_engine() -> Engine:
    return create_database_engine(get_settings())


def create_database_engine(settings: Settings) -> Engine:
    connect_args = (
        {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
    )
    return create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)


def initialize_database(settings: Settings | None = None) -> None:
    """Create the local schema on first start of the standalone application."""
    application_data_dir().mkdir(parents=True, exist_ok=True)
    engine = create_database_engine(settings or get_settings())
    try:
        Base.metadata.create_all(engine)
    finally:
        engine.dispose()


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    with get_session_factory()() as session:
        yield session
