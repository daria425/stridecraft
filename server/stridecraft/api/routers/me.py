import logging

from fastapi import APIRouter, BackgroundTasks, Response

from stridecraft.api.deps import CurrentUser, DbSession, GameContent, State
from stridecraft.api.errors import NEEDS_LOGIN, NO_STRIDER
from stridecraft.api.schemas import AdoptIn, MeOut, ProfileOut, StriderOut, SyncStatusOut
from stridecraft.db.repositories import RunRepository, StriderRepository, UserRepository
from stridecraft.errors import NoStriderError
from stridecraft.models import Strider, User
from stridecraft.services.adoption import AdoptionService
from stridecraft.services.reset import StriderReset
from stridecraft.stats.stats_calculator import Stats

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/me", tags=["me"], responses=NEEDS_LOGIN)


def strider_out(session: DbSession, user: User, strider: Strider) -> StriderOut:
    stats = Stats.total(RunRepository(session).gains(user.id))
    return StriderOut.of(strider, stats)


@router.get("", summary="Who is logged in, and do they have a strider yet")
def get_me(user: CurrentUser, session: DbSession) -> MeOut:
    """The first call the frontend makes. `strider: null` means: go to the adoption page."""
    strider = StriderRepository(session).get_for_user(user.id)
    return MeOut.of(user, strider and strider_out(session, user, strider))


@router.get("/strider", summary="The user's strider and its stats", responses=NO_STRIDER)
def get_strider(user: CurrentUser, session: DbSession) -> StriderOut:
    strider = StriderRepository(session).get_for_user(user.id)
    if strider is None:
        raise NoStriderError("Adopt a strider first")
    return strider_out(session, user, strider)


@router.post(
    "/strider",
    status_code=201,
    summary="Adopt a strider",
    description=(
        "One per user, once. The adoption time is now: only runs after it add to stats. This "
        "also starts importing the user's Strava runs in the background; follow it with "
        "`GET /me/sync`."
    ),
    responses={
        409: {"description": "The user already has a strider"},
        422: {"description": "Unknown breed or unusable name"},
    },
)
def adopt(
    body: AdoptIn,
    user: CurrentUser,
    session: DbSession,
    content: GameContent,
    state: State,
    background: BackgroundTasks,
) -> StriderOut:
    strider = AdoptionService(session, content).adopt(
        user, body.breed, body.name, waypoint_spacing_km=body.waypoint_spacing_km
    )
    session.commit()
    logger.info("User %s adopted %s the %s", user.id, strider.name, strider.breed)
    state.jobs.start(user.id)
    background.add_task(state.jobs.run, user.id, lambda: state.importer.import_for(user.id))
    return strider_out(session, user, strider)


@router.get("/profile", summary="Totals since adoption for the profile page", responses=NO_STRIDER)
def get_profile(user: CurrentUser, session: DbSession) -> ProfileOut:
    """Only runs counted after adoption, so a fresh strider starts at zero."""
    if StriderRepository(session).get_for_user(user.id) is None:
        raise NoStriderError("Adopt a strider first")
    return ProfileOut.of(RunRepository(session).totals_since_adoption(user.id))


@router.delete(
    "/strider",
    status_code=204,
    summary="Reset the profile: remove the strider and start onboarding over",
    description=(
        "Deletes the strider, its journey, all stored runs and the sync time. The user stays "
        "logged in with their Strava login, so the next `GET /me` has `strider: null` and the "
        "frontend sends them to adoption. Cannot be undone."
    ),
    responses={**NO_STRIDER, 409: {"description": "An import is running"}},
)
def reset_profile(user: CurrentUser, session: DbSession, state: State) -> Response:
    state.jobs.forget(user.id)
    StriderReset(session).reset(user)
    session.commit()
    logger.info("User %s reset their profile: strider, journey and runs deleted", user.id)
    return Response(status_code=204)


@router.get("/sync", summary="How the Strava import is going")
def get_sync(user: CurrentUser, session: DbSession, state: State) -> SyncStatusOut:
    # Re-read the user: `last_synced_at` is written by the background import.
    fresh = UserRepository(session).get(user.id)
    return SyncStatusOut.of(state.jobs.status(user.id), fresh)


@router.post(
    "/sync",
    status_code=202,
    summary="Import new runs from Strava now",
    responses={**NO_STRIDER, 409: {"description": "An import is already running"}},
)
def start_sync(
    user: CurrentUser, session: DbSession, state: State, background: BackgroundTasks
) -> SyncStatusOut:
    if StriderRepository(session).get_for_user(user.id) is None:
        raise NoStriderError("Adopt a strider before syncing")
    logger.info("User %s asked for a sync", user.id)
    state.jobs.start(user.id)
    background.add_task(state.jobs.run, user.id, lambda: state.importer.import_for(user.id))
    return SyncStatusOut.of(state.jobs.status(user.id), user)
