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
    training_default: bool
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
            training_default=payload.get("workout_type") in TRAINING_WORKOUT_TYPES,
            best_efforts=[BestEffort.from_strava(e) for e in payload.get("best_efforts") or []],
        )
