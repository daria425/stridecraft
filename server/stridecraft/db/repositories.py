"""Read and write the tables, converting to and from the domain objects in stridecraft/models.py.

Repositories never commit: the caller decides what belongs in one transaction.
"""

from dataclasses import asdict
from datetime import datetime

from cryptography.fernet import Fernet
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from stridecraft.db.tables import RunGainRow, RunRow, StravaTokenRow, StriderRow, UserRow
from stridecraft.errors import AlreadyAdoptedError
from stridecraft.models import BestEffort, Run, Strider, User
from stridecraft.stats.stats_calculator import RunGains
from stridecraft.strava.auth import Tokens


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, user_id: int) -> User | None:
        return self.to_user(self.session.get(UserRow, user_id))

    def first(self) -> User | None:
        """The only user, while there is just the author."""
        return self.to_user(self.session.scalar(select(UserRow).order_by(UserRow.id)))

    def get_by_strava_id(self, strava_athlete_id: int) -> User | None:
        row = self.session.scalar(select(UserRow).filter_by(strava_athlete_id=strava_athlete_id))
        return self.to_user(row)

    def create(
        self,
        strava_athlete_id: int,
        username: str | None = None,
        firstname: str | None = None,
        profile_url: str | None = None,
    ) -> User:
        row = UserRow(
            strava_athlete_id=strava_athlete_id,
            username=username,
            firstname=firstname,
            profile_url=profile_url,
        )
        self.session.add(row)
        self.session.flush()
        return self.to_user(row)

    def upsert_profile(
        self,
        strava_athlete_id: int,
        username: str | None,
        firstname: str | None,
        profile_url: str | None,
    ) -> User:
        """The user for this Strava athlete, created on first login, profile refreshed on every
        one. Two simultaneous first logins end up with one user, not an error."""
        row = self.session.scalar(select(UserRow).filter_by(strava_athlete_id=strava_athlete_id))
        if row is None:
            try:
                with self.session.begin_nested():
                    return self.create(strava_athlete_id, username, firstname, profile_url)
            except IntegrityError:  # the other login won the race
                row = self.session.scalar(
                    select(UserRow).filter_by(strava_athlete_id=strava_athlete_id)
                )
        row.username, row.firstname, row.profile_url = username, firstname, profile_url
        self.session.flush()
        return self.to_user(row)

    def mark_synced(self, user_id: int, synced_at: datetime) -> None:
        self.session.get(UserRow, user_id).last_synced_at = synced_at

    @staticmethod
    def to_user(row: UserRow | None) -> User | None:
        if row is None:
            return None
        return User(
            row.id,
            row.strava_athlete_id,
            row.username,
            row.firstname,
            row.profile_url,
            row.last_synced_at,
        )


class StriderRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_for_user(self, user_id: int) -> Strider | None:
        row = self.session.scalar(select(StriderRow).filter_by(user_id=user_id))
        if row is None:
            return None
        return Strider(row.id, row.user_id, row.breed, row.name, row.adopted_at)

    def create(self, user_id: int, breed: str, name: str, adopted_at: datetime) -> Strider:
        row = StriderRow(user_id=user_id, breed=breed, name=name, adopted_at=adopted_at)
        try:
            with self.session.begin_nested():
                self.session.add(row)
        except IntegrityError as error:  # a double click got there first
            raise AlreadyAdoptedError("This user already has a strider") from error
        return Strider(row.id, row.user_id, row.breed, row.name, row.adopted_at)


class TokenRepository:
    """Strava tokens per user, encrypted at rest with the app's Fernet key."""

    def __init__(self, session: Session, cipher: Fernet):
        self.session = session
        self.cipher = cipher

    def get(self, user_id: int) -> Tokens | None:
        row = self.session.get(StravaTokenRow, user_id)
        if row is None:
            return None
        return Tokens(
            self.decrypt(row.access_token), self.decrypt(row.refresh_token), row.expires_at
        )

    def save(self, user_id: int, tokens: Tokens) -> None:
        row = self.session.get(StravaTokenRow, user_id) or StravaTokenRow(user_id=user_id)
        row.access_token = self.encrypt(tokens.access_token)
        row.refresh_token = self.encrypt(tokens.refresh_token)
        row.expires_at = tokens.expires_at
        self.session.add(row)
        self.session.flush()

    def encrypt(self, text: str) -> str:
        return self.cipher.encrypt(text.encode()).decode()

    def decrypt(self, text: str) -> str:
        return self.cipher.decrypt(text.encode()).decode()


class RunRepository:
    def __init__(self, session: Session):
        self.session = session

    def history(self, user_id: int) -> list[Run]:
        """Every stored run (baseline and after adoption), oldest first."""
        rows = self.session.scalars(
            select(RunRow).filter_by(user_id=user_id).order_by(RunRow.start_time)
        )
        return [self.to_run(row) for row in rows]

    def known_source_ids(self, user_id: int, source: str) -> set[str]:
        return set(
            self.session.scalars(select(RunRow.source_id).filter_by(user_id=user_id, source=source))
        )

    def add(self, run: Run, gains: RunGains | None, computed_at: datetime) -> None:
        """Store a run; `gains=None` marks it as a baseline run (before adoption)."""
        row = RunRow(
            user_id=run.user_id,
            source=run.source,
            source_id=run.source_id,
            start_time=run.start_time,
            distance_m=run.distance_m,
            moving_time_s=run.moving_time_s,
            elevation_gain_m=run.elevation_gain_m,
            is_training=run.is_training,
            best_efforts=[asdict(effort) for effort in run.best_efforts],
        )
        if gains is not None:
            row.gains = RunGainRow(
                speed=gains.speed,
                endurance=gains.endurance,
                hills=gains.hills,
                consistency=gains.consistency,
                computed_at=computed_at,
            )
        self.session.add(row)
        self.session.flush()

    def gains(self, user_id: int) -> list[RunGains]:
        query = (
            select(RunRow.source_id, RunGainRow)
            .join(RunGainRow, RunGainRow.run_id == RunRow.id)
            .where(RunRow.user_id == user_id)
            .order_by(RunRow.start_time)
        )
        return [
            RunGains(source_id, gain.speed, gain.endurance, gain.hills, gain.consistency)
            for source_id, gain in self.session.execute(query)
        ]

    @staticmethod
    def to_run(row: RunRow) -> Run:
        return Run(
            user_id=row.user_id,
            source=row.source,
            source_id=row.source_id,
            start_time=row.start_time,
            distance_m=row.distance_m,
            moving_time_s=row.moving_time_s,
            elevation_gain_m=row.elevation_gain_m,
            is_training=row.is_training,
            best_efforts=[BestEffort(**effort) for effort in row.best_efforts or []],
        )
