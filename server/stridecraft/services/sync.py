from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from stridecraft.config import STATS_WINDOW_DAYS
from stridecraft.db.repositories import RunRepository, StriderRepository, UserRepository
from stridecraft.errors import NoStriderError, RateLimitError
from stridecraft.models import Run, Strider, User
from stridecraft.stats.stats_calculator import StatConverter
from stridecraft.strava.client import StravaClient

SOURCE = "strava"
# Best efforts need one detail request per run, and Strava allows ~100 requests per 15 minutes.
# Stats never need them (the activity list has distance, time, elevation and tag), so only the
# newest runs after adoption get the call; older ones are stored without best efforts.
DETAIL_CAP = 50
# Look this far back past the last sync, so a run uploaded late (watch syncing days after the
# run) is still picked up. Cheap: stored runs are skipped before any detail call is made.
SYNC_OVERLAP = timedelta(days=7)


@dataclass(frozen=True)
class SyncResult:
    new_runs: int  # runs stored by this sync
    baseline_runs: int  # of those, how many were before adoption (no gains)
    detailed_runs: int  # of those, how many have best efforts
    truncated: bool = False  # True if the oldest runs were left out (away for very long)


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
        # Oldest first: each run's baseline needs the runs before it already stored.
        listing = self.client.new_summaries(
            int(after.timestamp()), known, before_epoch=int(started.timestamp()) + 1
        )
        found = sorted(
            ((summary, Run.from_strava(summary, user.id)) for summary in listing.summaries),
            key=lambda pair: pair[1].start_time,
        )
        detail_ids = self.newest_gps_ids(found, strider.adopted_at)

        history = self.runs.history(user.id)
        baseline = detailed = 0
        for summary, run in found:
            if summary["id"] in detail_ids:
                run = self.with_best_efforts(summary, run, user.id, detail_ids)
            detailed += bool(run.best_efforts)
            baseline += self.store(run, strider, history, started)
            history.append(run)

        self.users.mark_synced(user.id, started)
        self.session.commit()
        return SyncResult(len(found), baseline, detailed, listing.truncated)

    @staticmethod
    def newest_gps_ids(found: list[tuple[dict, Run]], adopted_at: datetime) -> set[int]:
        """Ids of the newest DETAIL_CAP GPS runs from adoption on (treadmill has no efforts)."""
        wanted = [
            summary["id"]
            for summary, run in reversed(found)
            if not summary.get("trainer") and run.start_time >= adopted_at
        ]
        return set(wanted[:DETAIL_CAP])

    def with_best_efforts(self, summary: dict, run: Run, user_id: int, detail_ids: set[int]) -> Run:
        """The run rebuilt from its detailed activity, or as is if Strava says to slow down."""
        try:
            return Run.from_strava(self.client.activity_detail(summary["id"]), user_id)
        except RateLimitError:
            detail_ids.clear()  # stop asking: the stats do not depend on best efforts
            return run

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
