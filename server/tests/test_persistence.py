from datetime import UTC, datetime, timedelta

import pytest

from stridecraft.db.repositories import RunRepository, StriderRepository, UserRepository
from stridecraft.models import BestEffort, Run
from stridecraft.services.adoption import AdoptionError, AdoptionService
from stridecraft.services.sync import NoStriderError, SyncService
from stridecraft.stats.stats_calculator import StatConverter, Stats
from stridecraft.utils.names import MAX_NAME_LENGTH, random_name

ADOPTED = datetime(2026, 1, 1, tzinfo=UTC)


def activity(days_after_adoption: float, km: float = 10, elevation: float = 0, **extra) -> dict:
    """A Strava activity payload starting `days_after_adoption` days from ADOPTED."""
    start = ADOPTED + timedelta(days=days_after_adoption)
    return {
        "id": int(start.timestamp()),
        "start_date": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "distance": km * 1000,
        "moving_time": int(km * 6 * 60),
        "total_elevation_gain": elevation,
        **extra,
    }


class FakeStrava:
    """Behaves like StravaClient.fetch_activities: honours `after` and skips stored ids."""

    def __init__(self, *activities: dict):
        self.activities = list(activities)
        self.calls: list[tuple[datetime, set[str]]] = []

    def fetch_activities(self, after_epoch: int, skip_ids=frozenset()) -> list[dict]:
        self.calls.append((datetime.fromtimestamp(after_epoch, UTC), set(skip_ids)))
        return [
            a
            for a in self.activities
            if int(datetime.fromisoformat(a["start_date"]).timestamp()) >= after_epoch
            and str(a["id"]) not in skip_ids
        ]


class Setup:
    """A user with a strider adopted at ADOPTED and a sync service on a fake Strava."""

    def __init__(self, session, user, content, fake: FakeStrava, now: datetime):
        self.session, self.user, self.fake = session, user, fake
        self.now = now
        AdoptionService(session, content).adopt(user, "cetus", "Achilles", ADOPTED)
        session.commit()
        self.sync_service = SyncService(fake, session, clock=lambda: self.now)

    def sync(self):
        user = UserRepository(self.session).get(self.user.id)
        return self.sync_service.sync(user)

    def stats(self) -> Stats:
        return Stats.total(RunRepository(self.session).gains(self.user.id))


@pytest.fixture
def make_setup(session, user, content):
    def make(*activities, now=ADOPTED + timedelta(days=30)):
        return Setup(session, user, content, FakeStrava(*activities), now)

    return make


def test_only_runs_after_adoption_earn_gains_and_stats_match_the_calculator(make_setup, session):
    setup = make_setup(
        activity(-3, km=20),  # baseline: stored, no gains
        activity(1),
        activity(2, elevation=120),
        activity(3, workout_type=3),
    )
    result = setup.sync()

    runs = RunRepository(session)
    stored = runs.history(setup.user.id)
    assert (result.new_runs, result.baseline_runs) == (4, 1)
    assert len(stored) == 4
    assert len(runs.gains(setup.user.id)) == 3
    assert setup.stats() == StatConverter().convert(stored, ADOPTED).stats
    assert setup.stats().speed > Stats().speed


def test_syncing_again_changes_nothing(make_setup):
    setup = make_setup(activity(1), activity(2), activity(3))
    setup.sync()
    stats_before = setup.stats()

    again = setup.sync()

    assert again.new_runs == 0
    assert setup.stats() == stats_before


def test_runs_in_one_batch_build_on_each_other(make_setup, session):
    """Third run of the week completes the weekly goal: needs the first two as history."""
    start = 7 - ADOPTED.weekday()  # next Monday after adoption, so all three share a week
    setup = make_setup(activity(start), activity(start + 1), activity(start + 2))
    setup.sync()

    consistency = [g.consistency for g in RunRepository(session).gains(setup.user.id)]
    assert consistency[:2] == [0, 0]
    assert consistency[2] > 0


def test_a_late_upload_does_not_rewrite_gains_already_stored(make_setup, session):
    later = activity(10, km=5)
    setup = make_setup(later, now=ADOPTED + timedelta(days=11))
    setup.sync()
    before = {g.source_id: g for g in RunRepository(session).gains(setup.user.id)}

    setup.fake.activities.append(activity(5, km=30))  # uploaded late, but started earlier
    setup.now += timedelta(days=1)
    setup.sync()

    after = {g.source_id: g for g in RunRepository(session).gains(setup.user.id)}
    assert len(after) == 2
    assert after[str(later["id"])] == before[str(later["id"])]


def test_first_sync_reaches_back_for_a_baseline_then_only_a_little_past_last_sync(make_setup):
    setup = make_setup(activity(1))
    setup.sync()
    setup.now += timedelta(days=3)
    setup.sync()

    (first_after, _), (second_after, skipped) = setup.fake.calls
    assert first_after < ADOPTED - timedelta(days=30)
    assert second_after > ADOPTED
    assert skipped  # stored runs are passed on so they cost no detail call


def test_cannot_sync_before_adopting(session, user):
    with pytest.raises(NoStriderError):
        SyncService(FakeStrava(), session).sync(user)


def test_run_survives_the_database_with_time_zone_and_best_efforts(session, user):
    run = Run(
        user_id=user.id,
        source="strava",
        source_id="9",
        start_time=datetime(2026, 3, 1, 7, 30, tzinfo=UTC),
        distance_m=5000,
        moving_time_s=1500,
        elevation_gain_m=12,
        is_training=True,
        best_efforts=[BestEffort("5k", 5000, 1500, 1)],
    )
    runs = RunRepository(session)
    runs.add(run, None, computed_at=ADOPTED)
    session.commit()

    assert runs.history(user.id) == [run]


def test_adoption_rules(session, user, content):
    service = AdoptionService(session, content)
    with pytest.raises(AdoptionError, match="Unknown breed"):
        service.adopt(user, "unicorn", "Bob")
    with pytest.raises(AdoptionError):
        service.adopt(user, "cetus", "   ")
    with pytest.raises(AdoptionError):
        service.adopt(user, "cetus", "x" * (MAX_NAME_LENGTH + 1))

    strider = service.adopt(user, "cetus", "  Hector ")
    assert strider.name == "Hector"
    assert StriderRepository(session).get_for_user(user.id) == strider
    with pytest.raises(AdoptionError, match="already"):
        service.adopt(user, "cetus", "Other")


def test_suggested_names_are_usable_names():
    from stridecraft.utils.names import clean_name

    for _ in range(50):
        name = random_name()
        assert clean_name(name) == name
