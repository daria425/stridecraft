from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from stridecraft.config import DATABASE_PATH
from stridecraft.db.tables import Base

IN_MEMORY_URL = "sqlite://"


class Database:
    """Owns the engine and creates the tables. Tests pass `IN_MEMORY_URL`."""

    def __init__(self, url: str = f"sqlite:///{DATABASE_PATH}"):
        self.url = url
        file = make_url(url).database
        self.path = Path(file) if file else None
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self.engine: Engine = create_engine(url, **self.engine_options(url))
        event.listen(self.engine, "connect", self.configure_connection)
        self.sessions = sessionmaker(self.engine, expire_on_commit=False)
        Base.metadata.create_all(self.engine)

    @staticmethod
    def engine_options(url: str) -> dict:
        """An in-memory database lives in one connection, which the API's request threads and
        the background import must share."""
        if make_url(url).database:
            return {}
        return {"poolclass": StaticPool, "connect_args": {"check_same_thread": False}}

    def configure_connection(self, connection, record) -> None:
        connection.execute("PRAGMA foreign_keys=ON")
        if self.path:
            # The background import writes while requests read: WAL lets them overlap, and the
            # timeout makes a second writer wait instead of failing with "database is locked".
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA busy_timeout=5000")

    @contextmanager
    def session(self) -> Iterator[Session]:
        with self.sessions() as session:
            yield session

    def wipe(self) -> None:
        """Delete the database file (the schema-change workflow, ADR-0006). Make a new `Database`
        afterwards: this one is closed."""
        self.engine.dispose()
        if self.path:
            self.path.unlink(missing_ok=True)
