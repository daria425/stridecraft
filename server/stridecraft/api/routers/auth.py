from fastapi import APIRouter, Request, Response
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import RedirectResponse

from stridecraft.api.deps import State
from stridecraft.api.state import AppState
from stridecraft.db.repositories import TokenRepository, UserRepository
from stridecraft.strava.auth import Tokens

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/strava/login", status_code=302, summary="Send the browser to Strava to log in")
async def login(request: Request, state: State) -> RedirectResponse:
    """A browser navigation, not a `fetch` call: point a link or `window.location` at it."""
    callback = f"{state.config.public_url}{request.app.url_path_for('callback')}"
    return await state.login.redirect(request, callback)


@router.get(
    "/strava/callback",
    status_code=302,
    summary="Where Strava sends the browser back to",
    description=(
        "Creates the user on first login, stores their Strava tokens, starts the session and "
        "redirects to the frontend. If login fails the redirect carries `?error=denied` (the "
        "user said no) or `?error=scope` (they did not allow reading their activities)."
    ),
)
async def callback(request: Request, state: State) -> RedirectResponse:
    outcome = await state.login.finish(request)
    if isinstance(outcome, str):
        return RedirectResponse(f"{state.config.frontend_url}?error={outcome}", status_code=302)
    athlete, tokens = outcome
    request.session["user_id"] = await run_in_threadpool(sign_in, state, athlete, tokens)
    return RedirectResponse(state.config.frontend_url, status_code=302)


def sign_in(state: AppState, athlete: dict, tokens: Tokens) -> int:
    """Create-or-get the user for this Strava athlete (refreshing their profile) and save their
    tokens. Returns the user id."""
    with state.database.session() as session:
        user = UserRepository(session).upsert_profile(
            athlete["id"], athlete.get("username"), athlete.get("firstname"), athlete.get("profile")
        )
        TokenRepository(session, state.cipher).save(user.id, tokens)
        session.commit()
        return user.id


@router.post("/logout", status_code=204, summary="End the session")
def logout(request: Request) -> Response:
    request.session.clear()
    return Response(status_code=204)
