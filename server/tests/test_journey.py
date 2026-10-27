import random
from datetime import UTC, datetime, timedelta
from itertools import groupby

import pytest

from stridecraft.content.models import Encounter, Journey, Landmark, Leg
from stridecraft.db.repositories import JourneyEventRepository, RunRepository
from stridecraft.errors import AdoptionError
from stridecraft.models import Run
from stridecraft.services.adoption import (
    MAX_WAYPOINT_SPACING_KM,
    MIN_WAYPOINT_SPACING_KM,
    AdoptionService,
)
from stridecraft.services.journey import NO_REPEAT_WINDOW, EncounterRoller, JourneyService, Road
from stridecraft.stats.stats_calculator import RunGains

ADOPTED = datetime(2026, 1, 1, tzinfo=UTC)


class Traveller:
    """A user with a strider, who can run N km at a time."""

    def __init__(self, session, user, content, spacing=None):
        self.session, self.user, self.content = session, user, content
        self.strider = AdoptionService(session, content).adopt(
            user, "cetus", "Achilles", ADOPTED, spacing
        )
        self.service = JourneyService(session, content, random.Random(1))
        self.runs = RunRepository(session)
        self.count = 0

    def run(self, km: float, baseline: bool = False):
        """Store a run of `km` and let the journey react, like a sync would."""
        self.count += 1
        when = ADOPTED + timedelta(days=-1 if baseline else self.count)
        run = Run(self.user.id, "strava", f"r{self.count}", when, km * 1000, 3000, 0.0, False)
        gains = None if baseline else RunGains(run.source_id, 0, 0, 0, 0)
        run_id = self.runs.add(run, gains, ADOPTED)
        return self.service.record(self.strider, run_id, run) if gains else []

    def events(self):
        return JourneyEventRepository(self.session).newest_first(self.user.id)


@pytest.fixture
def traveller(session, user, content):
    return Traveller(session, user, content)


def test_km_to_go_shrinks_with_each_run_and_a_waypoint_needs_the_whole_spacing(traveller):
    spacing = traveller.strider.waypoint_spacing_km
    assert traveller.run(spacing * 0.6) == []
    assert traveller.service.progress(traveller.strider).km_to_go == pytest.approx(spacing * 0.4)

    assert len(traveller.run(spacing * 0.4)) == 1  # landing exactly on the mark counts


def test_overshoot_is_not_lost_so_the_next_waypoint_stays_on_the_grid(traveller):
    spacing = traveller.strider.waypoint_spacing_km
    crossed = traveller.run(spacing * 2.5)  # one long run crosses two waypoints
    assert [e.waypoint_number for e in crossed] == [1, 2]
    assert [e.threshold_km for e in crossed] == [spacing, spacing * 2]
    assert traveller.service.progress(traveller.strider).km_to_go == pytest.approx(spacing * 0.5)

    (third,) = traveller.run(spacing * 0.5)
    assert third.threshold_km == spacing * 3


def test_runs_before_adoption_do_not_move_the_strider(traveller):
    assert traveller.run(500, baseline=True) == []
    assert traveller.service.progress(traveller.strider).total_km == 0


def test_recording_twice_crosses_nothing_new(traveller):
    spacing = traveller.strider.waypoint_spacing_km
    traveller.run(spacing)
    run = Run(traveller.user.id, "strava", "r1", ADOPTED, spacing * 1000, 3000, 0.0, False)
    assert traveller.service.record(traveller.strider, 1, run) == []
    assert len(traveller.events()) == 1


def test_legs_follow_one_another_each_ends_in_its_landmark_and_the_road_loops(traveller):
    spacing = traveller.strider.waypoint_spacing_km
    journey = traveller.content.journey
    legs = {leg.id: leg for leg in journey.legs}
    traveller.run(spacing * sum(leg.length for leg in journey.legs) * 3)  # several laps

    events = sorted(traveller.events(), key=lambda e: e.waypoint_number)
    stretches = [list(group) for _, group in groupby(events, key=lambda e: e.leg_id)]

    assert stretches[0][0].leg_id == journey.legs[0].id  # the road starts in the first leg
    for stretch in stretches:
        leg = legs[stretch[0].leg_id]
        assert len(stretch) == leg.length
        assert [e.kind for e in stretch] == ["encounter"] * (leg.length - 1) + ["landmark"]
    leg_order = [stretch[0].leg_id for stretch in stretches]
    assert all(a != b for a, b in zip(leg_order, leg_order[1:], strict=False))
    assert set(leg_order) == set(legs)  # every leg gets its turn, so every tag is seen
    for stretch, following in zip(stretches, stretches[1:], strict=False):
        assert stretch[-1].next_leg_id == following[0].leg_id


def test_a_road_of_one_leg_loops_that_leg():
    leg = Leg(id="a", name="A", tags=["t"], length=2, landmark=Landmark(name="L", text="x"))
    road = Road(Journey(id="j", name="J", intro="x", legs=[leg]), random.Random(0))
    assert road.draw_next_leg(leg) == leg


def test_the_landmark_of_the_current_leg_is_announced_before_it_is_reached(traveller):
    spacing = traveller.strider.waypoint_spacing_km
    legs = {leg.name: leg for leg in traveller.content.journey.legs}
    first = traveller.service.progress(traveller.strider)
    assert first.landmark.km_to_go == spacing * legs[first.leg_name].length

    traveller.run(spacing * legs[first.leg_name].length)  # finish the first leg
    after = traveller.service.progress(traveller.strider)
    assert after.leg_name != first.leg_name
    assert after.landmark.km_to_go == spacing * legs[after.leg_name].length


def test_scenes_are_filled_in_and_do_not_repeat_within_the_window(traveller):
    traveller.run(traveller.strider.waypoint_spacing_km * 60)
    events = sorted(traveller.events(), key=lambda e: e.waypoint_number)
    scenes = [e for e in events if e.kind == "encounter"]

    assert all("{" not in e.text and "}" not in e.text for e in events)
    assert any("Achilles" in e.text for e in events)
    for index, scene in enumerate(scenes):
        previous = {s.source_id for s in scenes[max(0, index - NO_REPEAT_WINDOW) : index]}
        assert scene.source_id not in previous


@pytest.mark.parametrize("pool_size", [1, 2])
def test_a_tiny_pool_still_rolls(pool_size):
    pool = {
        f"e{i}": Encounter(id=f"e{i}", name="E", text="x", tags=["t"]) for i in range(pool_size)
    }
    roller = EncounterRoller(pool, random.Random(0))
    recent: list[str] = []
    for _ in range(10):
        scene = roller.roll(["t"], recent, {})
        if pool_size > 1:
            assert scene.source_id not in recent[:1]
        recent.insert(0, scene.source_id)


def test_the_heavier_encounter_is_rolled_more_often():
    pool = {
        "rare": Encounter(id="rare", name="R", text="x", tags=["t"], weight=1),
        "common": Encounter(id="common", name="C", text="x", tags=["t"], weight=50),
    }
    roller = EncounterRoller(pool, random.Random(0))
    seen = [roller.roll(["t"], [], {}).source_id for _ in range(200)]
    assert seen.count("common") > seen.count("rare")


@pytest.mark.parametrize("bad", [MIN_WAYPOINT_SPACING_KM - 1, MAX_WAYPOINT_SPACING_KM + 1, 0, -50])
def test_waypoint_spacing_outside_its_bounds_is_refused(session, user, content, bad):
    with pytest.raises(AdoptionError, match="waypoints"):
        AdoptionService(session, content).adopt(user, "cetus", "Achilles", ADOPTED, bad)


@pytest.mark.parametrize("ok", [MIN_WAYPOINT_SPACING_KM, MAX_WAYPOINT_SPACING_KM])
def test_the_spacing_bounds_themselves_are_allowed(session, user, content, ok):
    strider = AdoptionService(session, content).adopt(user, "cetus", "Achilles", ADOPTED, ok)
    assert strider.waypoint_spacing_km == ok


def test_a_larger_spacing_moves_through_the_same_story_more_slowly(session, user, content):
    slow = Traveller(session, user, content, spacing=500)
    assert len(slow.run(499)) == 0
    assert len(slow.run(1)) == 1
