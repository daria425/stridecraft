"""Only registered when `DEV_TOOLS=1` (see `create_app`); not part of the product."""

import logging

from fastapi import APIRouter, Response

from stridecraft.api.deps import CurrentUser, DbSession, State
from stridecraft.api.errors import NEEDS_LOGIN, NO_STRIDER
from stridecraft.services.reset import StriderReset

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/me", tags=["dev"], responses=NEEDS_LOGIN)


@router.delete(
    "/strider",
    status_code=204,
    summary="Dev: remove the strider and start onboarding over",
    description=(
        "Deletes the strider, all stored runs and the sync time. The user stays logged in with "
        "their Strava login, so the next `GET /me` has `strider: null`."
    ),
    responses={**NO_STRIDER, 409: {"description": "An import is running"}},
)
def delete_strider(user: CurrentUser, session: DbSession, state: State) -> Response:
    state.jobs.forget(user.id)
    StriderReset(session).reset(user)
    session.commit()
    logger.info("User %s started over: strider and runs deleted", user.id)
    return Response(status_code=204)
