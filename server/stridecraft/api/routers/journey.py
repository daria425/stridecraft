from fastapi import APIRouter

from stridecraft.api.deps import CurrentUser, DbSession, GameContent
from stridecraft.api.errors import NEEDS_LOGIN, NO_STRIDER
from stridecraft.api.schemas import JourneyOut
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
