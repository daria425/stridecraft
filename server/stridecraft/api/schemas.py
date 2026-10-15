"""What the API sends and receives. Separate from the domain objects in stridecraft/models.py."""

from datetime import datetime

from pydantic import BaseModel, Field

from stridecraft.models import Strider, User
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
    stats: StatsOut

    @classmethod
    def of(cls, strider: Strider, stats: Stats) -> "StriderOut":
        return cls(
            name=strider.name,
            breed=strider.breed,
            adopted_at=strider.adopted_at,
            stats=StatsOut.of(stats),
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
    name: str = Field(examples=["Aura"], description="Up to 30 characters.")


class BreedOut(BaseModel):
    id: str
    name: str
    description: str
    model: str | None


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
