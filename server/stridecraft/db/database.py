from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

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
        self.engine: Engine = create_engine(url)
        event.listen(self.engine, "connect", self.enable_foreign_keys)
        self.sessions = sessionmaker(self.engine, expire_on_commit=False)
        Base.metadata.create_all(self.engine)

    @staticmethod
    def enable_foreign_keys(connection, record) -> None:
        connection.execute("PRAGMA foreign_keys=ON")

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
