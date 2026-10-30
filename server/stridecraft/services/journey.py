"""The journey (ADR-0017): distance moves the strider along an endless road, a waypoint every
`waypoint_spacing_km`. Distance is derived from the runs, never stored; what is stored is each
crossing, with the scene it became and, at a landmark, the leg rolled to come next. All of it is
rolled once and frozen.
"""

import random
from dataclasses import dataclass

from sqlalchemy.orm import Session

from stridecraft.content.models import Encounter, Journey, Leg
from stridecraft.content.registry import Content
from stridecraft.db.repositories import JourneyEventRepository, RunRepository
from stridecraft.models import JourneyEvent, Run, Strider
from stridecraft.utils.templates import fill

# A scene is not repeated until this many others have happened (fewer if the pool is tiny).
NO_REPEAT_WINDOW = 4


@dataclass(frozen=True)
class Stop:
    leg: Leg
    index: int  # 1 for the first waypoint of the leg

    @property
    def is_landmark(self) -> bool:
        return self.index >= self.leg.length  # `>=` so shortening a leg later cannot strand anyone


class Road:
    """Where the next waypoint is. The road starts in the first leg; after each landmark the next
    leg is drawn from the others (the same one again only if it is the only leg)."""

    def __init__(self, journey: Journey, rng: random.Random):
        self.first = journey.legs[0]
        self.legs = {leg.id: leg for leg in journey.legs}
        self.rng = rng

    def next_stop(self, last: JourneyEvent | None) -> Stop:
        """The stop after the last crossing, or the start of the road if there is none."""
        if last is None:
            return Stop(self.first, 1)
        if last.kind == "landmark":
            return Stop(self.legs.get(last.next_leg_id, self.first), 1)
        leg = self.legs.get(last.leg_id)
        return Stop(leg, last.leg_waypoint + 1) if leg else Stop(self.first, 1)

    def draw_next_leg(self, finished: Leg) -> Leg:
        others = [leg for leg in self.legs.values() if leg.id != finished.id]
        return self.rng.choice(others or [finished])


@dataclass(frozen=True)
class Scene:
    kind: str  # "encounter" or "landmark"
    source_id: str
    title: str
    text: str


class EncounterRoller:
    """Picks a scene for a waypoint: an encounter that fits the leg, not one seen very lately,
    weighted, with each of its slots filled by a random value."""

    def __init__(self, encounters: dict[str, Encounter], rng: random.Random | None = None):
        self.encounters = encounters
        self.rng = rng or random.Random()

    def roll(self, tags: list[str], recent_ids: list[str], context: dict[str, str]) -> Scene:
        pool = [e for e in self.encounters.values() if set(e.tags) & set(tags)]
        window = set(recent_ids[: min(NO_REPEAT_WINDOW, len(pool) - 1)])
        fresh = [e for e in pool if e.id not in window]
        chosen = self.rng.choices(fresh, weights=[e.weight for e in fresh])[0]
        values = {slot: self.rng.choice(options) for slot, options in chosen.variables.items()}
        return Scene("encounter", chosen.id, chosen.name, fill(chosen.text, {**context, **values}))


@dataclass(frozen=True)
class LandmarkAhead:
    name: str
    km_to_go: float


@dataclass(frozen=True)
class JourneyProgress:
    intro: str
    total_km: float
    spacing_km: int
    leg_name: str  # the leg the next waypoint is in
    leg_length: int  # waypoints in that leg, the last being its landmark
    leg_waypoint: int  # which of them is next: 1 for the first
    km_to_go: float  # to the next waypoint
    landmark: LandmarkAhead  # the end of this leg
    crossed: list[JourneyEvent]  # newest first
    seen_waypoint: int  # the highest crossing already shown to the user


class JourneyService:
    def __init__(
        self, session: Session, content: Content, rng: random.Random | None = None
    ) -> None:
        self.content = content
        rng = rng or random.Random()
        self.road = Road(content.journey, rng)
        self.events = JourneyEventRepository(session)
        self.runs = RunRepository(session)
        self.roller = EncounterRoller(content.encounters, rng)

    def record(self, strider: Strider, run_id: int, run: Run) -> list[JourneyEvent]:
        """Cross every waypoint the strider's total distance has now reached. Call it right
        after a run with gains is stored. Safe to repeat: it only crosses what is not crossed."""
        total_m = self.runs.journey_metres(strider.user_id)
        last = self.events.latest(strider.user_id)
        number = last.waypoint_number if last else 0
        threshold = last.threshold_km if last else 0
        stop = self.road.next_stop(last)
        context = self.context(strider)
        crossed = []
        # Rounded to the millimetre so 49 999.9999 m of float noise does not miss a 50 km mark.
        while round(total_m, 3) >= (threshold + strider.waypoint_spacing_km) * 1000:
            number += 1
            threshold += strider.waypoint_spacing_km
            event = self.cross(strider, run_id, run, (number, threshold, stop), context)
            self.events.add(event)
            crossed.append(event)
            stop = self.road.next_stop(event)
        return crossed

    def cross(
        self,
        strider: Strider,
        run_id: int,
        run: Run,
        waypoint: tuple[int, int, Stop],
        context: dict[str, str],
    ) -> JourneyEvent:
        number, threshold, stop = waypoint
        next_leg_id = None
        if stop.is_landmark:
            landmark = stop.leg.landmark
            scene = Scene("landmark", stop.leg.id, landmark.name, fill(landmark.text, context))
            next_leg_id = self.road.draw_next_leg(stop.leg).id
        else:
            recent = self.events.recent_encounter_ids(strider.user_id, NO_REPEAT_WINDOW)
            scene = self.roller.roll(stop.leg.tags, recent, context)
        return JourneyEvent(
            user_id=strider.user_id,
            run_id=run_id,
            waypoint_number=number,
            leg_id=stop.leg.id,
            leg_waypoint=stop.index,
            next_leg_id=next_leg_id,
            kind=scene.kind,
            source_id=scene.source_id,
            title=scene.title,
            text=scene.text,
            threshold_km=threshold,
            crossed_at=run.start_time,
        )

    def progress(self, strider: Strider) -> JourneyProgress:
        total_km = self.runs.journey_metres(strider.user_id) / 1000
        crossed = self.events.newest_first(strider.user_id)
        stop = self.road.next_stop(crossed[0] if crossed else None)
        next_km = (crossed[0].threshold_km if crossed else 0) + strider.waypoint_spacing_km
        km_to_go = max(0.0, next_km - total_km)
        leg = stop.leg
        waypoints_after_next = max(0, leg.length - stop.index)
        return JourneyProgress(
            intro=fill(self.content.journey.intro, self.context(strider)),
            total_km=total_km,
            spacing_km=strider.waypoint_spacing_km,
            leg_name=leg.name,
            leg_length=leg.length,
            leg_waypoint=stop.index,
            km_to_go=km_to_go,
            landmark=LandmarkAhead(
                leg.landmark.name, km_to_go + waypoints_after_next * strider.waypoint_spacing_km
            ),
            crossed=crossed,
            seen_waypoint=strider.journey_seen_waypoint,
        )

    def context(self, strider: Strider) -> dict[str, str]:
        breed = self.content.breeds.get(strider.breed)
        return {"strider": strider.name, "breed": breed.name if breed else strider.breed}
