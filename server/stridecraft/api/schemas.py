"""What the API sends and receives. Separate from the domain objects in stridecraft/models.py."""

from datetime import datetime

from pydantic import BaseModel, Field

from stridecraft.models import JourneyEvent, RunTotals, Strider, User
from stridecraft.services.journey import JourneyProgress
from stridecraft.services.sync_jobs import SyncState, SyncStatus
from stridecraft.stats.stats_calculator import Stats


class ErrorOut(BaseModel):
    code: str = Field(examples=["no_strider"])
    message: str = Field(examples=["Adopt a strider before syncing"])


class StatsOut(BaseModel):
    speed: float
    endurance: float
    hills: float
    consistency: float

    @classmethod
    def of(cls, stats: Stats) -> "StatsOut":
        return cls(**vars(stats))


class StriderOut(BaseModel):
    name: str
    breed: str
    adopted_at: datetime
    waypoint_spacing_km: int
    stats: StatsOut

    @classmethod
    def of(cls, strider: Strider, stats: Stats) -> "StriderOut":
        return cls(
            name=strider.name,
            breed=strider.breed,
            adopted_at=strider.adopted_at,
            waypoint_spacing_km=strider.waypoint_spacing_km,
            stats=StatsOut.of(stats),
        )


class ProfileOut(BaseModel):
    runs: int = Field(description="Runs counted since adoption; earlier ones are baseline only.")
    total_km: float = Field(description="Voyage distance: runs counted since adoption.")
    elevation_gain_m: float = Field(description="Elevation gain, same runs.")
    training_runs: int = Field(description="Of those runs, how many Strava tagged Race or Workout.")

    @classmethod
    def of(cls, totals: RunTotals) -> "ProfileOut":
        return cls(
            runs=totals.runs,
            total_km=totals.distance_m / 1000,
            elevation_gain_m=totals.elevation_gain_m,
            training_runs=totals.training_runs,
        )


class MeOut(BaseModel):
    id: int
    username: str | None
    firstname: str | None
    profile_url: str | None
    strider: StriderOut | None = Field(
        description="`null` until the user adopts one: send them to the adoption page."
    )

    @classmethod
    def of(cls, user: User, strider: StriderOut | None) -> "MeOut":
        return cls(
            id=user.id,
            username=user.username,
            firstname=user.firstname,
            profile_url=user.profile_url,
            strider=strider,
        )


class AdoptIn(BaseModel):
    breed: str = Field(examples=["cetus"], description="An id from `GET /breeds`.")
    name: str | None = Field(
        default=None,
        examples=["Aura"],
        description=(
            "Up to 30 characters. Leave out to get a random one. The adoption page should "
            "prefill the field from `GET /names/random` and let the user edit it."
        ),
    )

    waypoint_spacing_km: int | None = Field(
        default=None,
        examples=[50],
        description=(
            "Kilometres between waypoints on the journey, 50 to 1000 (default 50). Smaller means "
            "faster progression through the same story: match it to your weekly mileage."
        ),
    )


class BreedOut(BaseModel):
    id: str
    name: str
    description: str
    model_url: str | None = Field(description="3D model URL, `null` if not made yet.")
    icon_url: str | None = Field(description="Still image URL for cards, `null` if not made yet.")


class NameOut(BaseModel):
    name: str


class SyncResultOut(BaseModel):
    new_runs: int
    baseline_runs: int = Field(description="Of the new runs, how many were before adoption.")
    detailed_runs: int = Field(description="Of the new runs, how many have best efforts.")
    truncated: bool = Field(description="True if the oldest runs were left out (away very long).")


class SyncStatusOut(BaseModel):
    state: SyncState
    last_synced_at: datetime | None
    last_result: SyncResultOut | None
    error: str | None = Field(description="Why the last import failed, in plain English.")

    @classmethod
    def of(cls, status: SyncStatus, user: User) -> "SyncStatusOut":
        result = status.result
        return cls(
            state=status.state,
            last_synced_at=user.last_synced_at,
            last_result=result and SyncResultOut(**vars(result)),
            error=status.error,
        )


class JourneyEventOut(BaseModel):
    waypoint_number: int
    kind: str = Field(description="`encounter` or `landmark`.")
    title: str
    text: str
    leg_id: str
    crossed_at: datetime = Field(description="When the run that crossed it started.")

    @classmethod
    def of(cls, event: JourneyEvent) -> "JourneyEventOut":
        return cls(
            waypoint_number=event.waypoint_number,
            kind=event.kind,
            title=event.title,
            text=event.text,
            leg_id=event.leg_id,
            crossed_at=event.crossed_at,
        )


class LandmarkAheadOut(BaseModel):
    name: str
    km_to_go: float


class JourneySeenIn(BaseModel):
    waypoint_number: int = Field(ge=0, description="The newest crossing the user has been shown.")


class JourneyOut(BaseModel):
    intro: str
    total_km: float = Field(description="Distance of every run since adoption.")
    spacing_km: int
    leg_name: str = Field(description="The leg the next waypoint is in.")
    leg_length: int = Field(description="Waypoints in that leg; the last one is its landmark.")
    leg_waypoint: int = Field(description="Which waypoint of the leg is next, 1 for the first.")
    km_to_go: float = Field(description="Distance to the next waypoint.")
    landmark: LandmarkAheadOut = Field(description="The end of the current leg.")
    crossed: list[JourneyEventOut] = Field(description="Newest first.")
    seen_waypoint: int = Field(
        description="The highest waypoint number already shown to the user; anything above it is "
        "new. Move it with `POST /me/journey/seen`."
    )

    @classmethod
    def of(cls, progress: JourneyProgress) -> "JourneyOut":
        return cls(
            intro=progress.intro,
            total_km=progress.total_km,
            spacing_km=progress.spacing_km,
            leg_name=progress.leg_name,
            leg_length=progress.leg_length,
            leg_waypoint=progress.leg_waypoint,
            km_to_go=progress.km_to_go,
            landmark=LandmarkAheadOut(**vars(progress.landmark)),
            crossed=[JourneyEventOut.of(event) for event in progress.crossed],
            seen_waypoint=progress.seen_waypoint,
        )
