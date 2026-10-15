"""SQLAlchemy tables. The domain objects live in stridecraft/models.py; repositories convert."""

from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator


class UtcDateTime(TypeDecorator):
    """SQLite drops time zones, so store naive UTC and hand back aware UTC."""

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("naive datetime: use timezone-aware (UTC) datetimes")
        return value.astimezone(UTC).replace(tzinfo=None)

    def process_result_value(self, value: datetime | None, dialect):
        return None if value is None else value.replace(tzinfo=UTC)


class Base(DeclarativeBase):
    pass


class UserRow(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    strava_athlete_id: Mapped[int] = mapped_column(unique=True)
    username: Mapped[str | None]
    firstname: Mapped[str | None]
    profile_url: Mapped[str | None]
    last_synced_at: Mapped[datetime | None] = mapped_column(UtcDateTime)


class StriderRow(Base):
    __tablename__ = "striders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)  # one per user
    breed: Mapped[str]  # an id from server/content/breeds/, deliberately not a foreign key
    name: Mapped[str]
    adopted_at: Mapped[datetime] = mapped_column(UtcDateTime)


class RunRow(Base):
    __tablename__ = "runs"
    __table_args__ = (
        UniqueConstraint("user_id", "source", "source_id"),
        Index("ix_runs_user_start", "user_id", "start_time"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    source: Mapped[str]
    source_id: Mapped[str]
    start_time: Mapped[datetime] = mapped_column(UtcDateTime)
    distance_m: Mapped[float]
    moving_time_s: Mapped[int]
    elevation_gain_m: Mapped[float]
    is_training: Mapped[bool]
    best_efforts: Mapped[list] = mapped_column(JSON, default=list)

    gains: Mapped["RunGainRow | None"] = relationship(back_populates="run", uselist=False)


class RunGainRow(Base):
    """What one post-adoption run added to each stat. Frozen: never recomputed (ADR-0003)."""

    __tablename__ = "run_gains"

    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"), primary_key=True)
    speed: Mapped[float]
    endurance: Mapped[float]
    hills: Mapped[float]
    consistency: Mapped[float]
    computed_at: Mapped[datetime] = mapped_column(UtcDateTime)

    run: Mapped[RunRow] = relationship(back_populates="gains")
