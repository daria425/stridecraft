from dataclasses import dataclass, field
from datetime import datetime

RUN_SPORT_TYPES = {"Run", "TrailRun"}
# Strava workout_type for runs: 0 default, 1 race, 2 long run, 3 workout.
TRAINING_WORKOUT_TYPES = {1, 3}


@dataclass(frozen=True)
class BestEffort:
    name: str
    distance_m: float
    elapsed_time_s: int
    pr_rank: int | None

    @classmethod
    def from_strava(cls, payload: dict) -> "BestEffort":
        return cls(
            name=payload["name"],
            distance_m=payload["distance"],
            elapsed_time_s=payload["elapsed_time"],
            pr_rank=payload.get("pr_rank"),
        )


@dataclass(frozen=True)
class Run:
    user_id: int
    source: str
    source_id: str
    start_time: datetime
    distance_m: float
    moving_time_s: int
    elevation_gain_m: float
    is_training: bool
    best_efforts: list[BestEffort] = field(default_factory=list)

    @classmethod
    def from_strava(cls, payload: dict, user_id: int) -> "Run":
        return cls(
            user_id=user_id,
            source="strava",
            source_id=str(payload["id"]),
            start_time=datetime.fromisoformat(payload["start_date"].replace("Z", "+00:00")),
            distance_m=payload["distance"],
            moving_time_s=payload["moving_time"],
            elevation_gain_m=payload.get("total_elevation_gain", 0.0),
            is_training=payload.get("workout_type") in TRAINING_WORKOUT_TYPES,
            best_efforts=[BestEffort.from_strava(e) for e in payload.get("best_efforts") or []],
        )


@dataclass(frozen=True)
class RunTotals:
    """What the strider has done since adoption: only runs that were counted, never baseline."""

    runs: int
    distance_m: float
    elevation_gain_m: float
    training_runs: int


@dataclass(frozen=True)
class User:
    """Identity and a small cache of the Strava profile; everything else stays in Strava."""

    id: int
    strava_athlete_id: int
    username: str | None
    firstname: str | None
    profile_url: str | None
    last_synced_at: datetime | None


@dataclass(frozen=True)
class Strider:
    """A user's creature. `adopted_at` is the sign-up date: only runs after it add to stats."""

    id: int
    user_id: int
    breed: str
    name: str
    adopted_at: datetime
    waypoint_spacing_km: int  # km between waypoints on the journey, chosen at adoption
    journey_seen_waypoint: int = 0  # the highest crossing the user has been shown


@dataclass(frozen=True)
class JourneyEvent:
    """A waypoint the strider crossed and what it turned into, as the user saw it."""

    user_id: int
    run_id: int
    waypoint_number: int
    leg_id: str
    leg_waypoint: int
    kind: str  # "encounter" or "landmark"
    source_id: str
    title: str
    text: str
    threshold_km: int
    crossed_at: datetime
    next_leg_id: str | None = None  # set on a landmark: where the road goes next
