from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from stridecraft.config import STATS_WINDOW_DAYS
from stridecraft.db.repositories import RunRepository, StriderRepository, UserRepository
from stridecraft.models import Run, Strider, User
from stridecraft.stats.stats_calculator import StatConverter
from stridecraft.strava.client import StravaClient

SOURCE = "strava"
# Look this far back past the last sync, so a run uploaded late (watch syncing days after the
# run) is still picked up. Cheap: stored runs are skipped before any detail call is made.
SYNC_OVERLAP = timedelta(days=7)


class NoStriderError(RuntimeError):
    pass


@dataclass(frozen=True)
class SyncResult:
    new_runs: int
    baseline_runs: int  # of the new runs, how many were before adoption (no gains)


class SyncService:
    """Turns new Strava runs into stored runs and frozen gains (journal/0006)."""

    def __init__(
        self,
        client: StravaClient,
        session: Session,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ):
        self.client = client
        self.clock = clock
        self.session = session
        self.users = UserRepository(session)
        self.striders = StriderRepository(session)
        self.runs = RunRepository(session)
        self.converter = StatConverter()

    def sync(self, user: User) -> SyncResult:
        strider = self.striders.get_for_user(user.id)
        if strider is None:
            raise NoStriderError("Adopt a strider before syncing")

        started = self.clock()
        known = self.runs.known_source_ids(user.id, SOURCE)
        after = self.fetch_start(user, strider.adopted_at)
        details = self.client.fetch_activities(int(after.timestamp()), known)
        new_runs = sorted(
            (Run.from_strava(detail, user.id) for detail in details), key=lambda r: r.start_time
        )

        history = self.runs.history(user.id)
        baseline = 0
        for run in new_runs:
            baseline += self.store(run, strider, history, started)
            history.append(run)

        self.users.mark_synced(user.id, started)
        self.session.commit()
        return SyncResult(len(new_runs), baseline)

    def store(self, run: Run, strider: Strider, history: list[Run], computed_at: datetime) -> bool:
        """Save the run; before adoption it is baseline only and gets no gains. Returns that."""
        is_baseline = run.start_time < strider.adopted_at
        gains = None
        if not is_baseline:
            gains = self.converter.gains_for(run, history, strider.adopted_at)
        self.runs.add(run, gains, computed_at)
        self.session.commit()  # a run and its gains land together or not at all
        return is_baseline

    @staticmethod
    def fetch_start(user: User, adopted_at: datetime) -> datetime:
        """First sync reaches back one stats window before adoption, to get the baseline."""
        if user.last_synced_at:
            return user.last_synced_at - SYNC_OVERLAP
        return adopted_at - timedelta(days=STATS_WINDOW_DAYS)
