from fastapi import APIRouter, Response

from stridecraft.api.deps import CurrentUser, DbSession, GameContent
from stridecraft.api.errors import NEEDS_LOGIN, NO_STRIDER
from stridecraft.api.schemas import JourneyOut, JourneySeenIn
from stridecraft.db.repositories import StriderRepository
from stridecraft.errors import NoStriderError
from stridecraft.services.journey import JourneyService

router = APIRouter(prefix="/me", tags=["journey"], responses=NEEDS_LOGIN)


@router.get(
    "/journey",
    summary="How far the strider has travelled and what it met on the way",
    responses=NO_STRIDER,
)
def get_journey(user: CurrentUser, session: DbSession, content: GameContent) -> JourneyOut:
    """Every run after adoption moves the strider along an endless road, a waypoint every
    `spacing_km`. Nothing here blocks or punishes: the road only ever goes forward."""
    strider = StriderRepository(session).get_for_user(user.id)
    if strider is None:
        raise NoStriderError("Adopt a strider first")
    return JourneyOut.of(JourneyService(session, content).progress(strider))


@router.post(
    "/journey/seen",
    status_code=204,
    summary="Record that the user has been shown crossings up to this waypoint",
    responses=NO_STRIDER,
)
def mark_journey_seen(
    body: JourneySeenIn, user: CurrentUser, session: DbSession, content: GameContent
) -> Response:
    """Call it once the banner for a new crossing has been dismissed. It only moves forward, and
    never past the newest crossing."""
    striders = StriderRepository(session)
    strider = striders.get_for_user(user.id)
    if strider is None:
        raise NoStriderError("Adopt a strider first")
    newest = JourneyService(session, content).progress(strider).crossed
    striders.mark_journey_seen(
        user.id, min(body.waypoint_number, newest[0].waypoint_number if newest else 0)
    )
    session.commit()
    return Response(status_code=204)
