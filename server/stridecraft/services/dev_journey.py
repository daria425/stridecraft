"""Dev tool: make the strider reach its next waypoint without running."""

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from stridecraft.content.registry import Content
from stridecraft.db.repositories import RunRepository, StriderRepository
from stridecraft.errors import NoStriderError
from stridecraft.models import JourneyEvent, Run, User
from stridecraft.services.journey import JourneyService
from stridecraft.stats.stats_calculator import RunGains

# A made-up run is slow and flat so it cannot look like anything in the pace baseline.
DEV_PACE_S_PER_KM = 600


class JourneyAdvancer:
    """Stores a made-up run exactly long enough to cross the next waypoint, with all-zero gains so
    no stat moves, then lets the journey react as a real sync would. The scene is genuinely
    rolled and frozen. `StriderReset` removes these runs with the rest."""

    def __init__(self, session: Session, content: Content):
        self.session = session
        self.journey = JourneyService(session, content)
        self.runs = RunRepository(session)

    def advance(self, user: User, waypoints: int = 1) -> list[JourneyEvent]:
        strider = StriderRepository(self.session).get_for_user(user.id)
        if strider is None:
            raise NoStriderError("Adopt a strider first")
        crossed: list[JourneyEvent] = []
        for _ in range(waypoints):
            km = self.journey.progress(strider).km_to_go
            crossed += self.run_for(user, strider, km)
        return crossed

    def run_for(self, user, strider, km: float) -> list[JourneyEvent]:
        source_id = f"dev-{uuid.uuid4().hex}"
        now = datetime.now(UTC)
        run = Run(
            user.id, "dev", source_id, now, km * 1000, round(km * DEV_PACE_S_PER_KM), 0.0, False
        )
        run_id = self.runs.add(run, RunGains(source_id, 0, 0, 0, 0), now)
        return self.journey.record(strider, run_id, run)
