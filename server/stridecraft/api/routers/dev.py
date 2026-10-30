"""Only registered when `DEV_TOOLS=1` (see `create_app`); not part of the product."""

import logging
from typing import Annotated

from fastapi import APIRouter, Query

from stridecraft.api.deps import CurrentUser, DbSession, GameContent
from stridecraft.api.errors import NEEDS_LOGIN, NO_STRIDER
from stridecraft.api.schemas import JourneyEventOut
from stridecraft.services.dev_journey import JourneyAdvancer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/me", tags=["dev"], responses=NEEDS_LOGIN)


@router.post(
    "/journey/advance",
    summary="Dev: cross the next waypoint(s) without running",
    description=(
        "Stores a made-up run of exactly the distance to the next waypoint (no stat gains) and "
        "records the crossing like a sync would. Reload the page to see it as a new arrival."
    ),
    responses=NO_STRIDER,
)
def advance_journey(
    user: CurrentUser,
    session: DbSession,
    content: GameContent,
    waypoints: Annotated[int, Query(ge=1, le=20)] = 1,
) -> list[JourneyEventOut]:
    crossed = JourneyAdvancer(session, content).advance(user, waypoints)
    session.commit()
    logger.info("User %s crossed %d waypoint(s) with dev runs", user.id, len(crossed))
    return [JourneyEventOut.of(event) for event in crossed]
