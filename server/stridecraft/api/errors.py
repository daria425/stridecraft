"""One place that turns the app's typed errors into HTTP responses (journal/0010)."""

from fastapi import Request
from fastapi.responses import JSONResponse

from stridecraft.api.schemas import ErrorOut
from stridecraft.errors import (
    AdoptionError,
    AlreadyAdoptedError,
    NoStriderError,
    NotAuthorizedError,
    NotLoggedInError,
    RateLimitError,
    StravaError,
    StridecraftError,
    SyncInProgressError,
)

# (status, code) per error class. The most specific class wins, so AlreadyAdoptedError (409)
# beats its parent AdoptionError (422).
HTTP_ERRORS: dict[type[StridecraftError], tuple[int, str]] = {
    NotLoggedInError: (401, "not_logged_in"),
    NotAuthorizedError: (403, "strava_reauth_required"),
    RateLimitError: (429, "strava_rate_limited"),
    StravaError: (502, "strava_unavailable"),
    NoStriderError: (404, "no_strider"),
    AlreadyAdoptedError: (409, "already_adopted"),
    AdoptionError: (422, "invalid_adoption"),
    SyncInProgressError: (409, "sync_in_progress"),
}
DEFAULT_ERROR = (500, "error")


def http_error_for(error: StridecraftError) -> tuple[int, str]:
    for cls in type(error).__mro__:
        if cls in HTTP_ERRORS:
            return HTTP_ERRORS[cls]
    return DEFAULT_ERROR


async def handle_stridecraft_error(request: Request, error: StridecraftError) -> JSONResponse:
    status, code = http_error_for(error)
    return JSONResponse({"code": code, "message": str(error)}, status_code=status)


# Shared by routes, so the OpenAPI spec shows the error body.
NEEDS_LOGIN: dict[int | str, dict] = {401: {"description": "Not logged in", "model": ErrorOut}}
NO_STRIDER: dict[int | str, dict] = {404: {"description": "No strider yet", "model": ErrorOut}}
