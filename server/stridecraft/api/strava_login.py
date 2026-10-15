from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from starlette.responses import RedirectResponse

from stridecraft.config import StravaConfig
from stridecraft.strava.auth import AUTHORIZE_URL, SCOPE, TOKEN_URL, Tokens

REQUIRED_SCOPE = SCOPE  # the user can untick it on Strava's consent screen


class StravaLogin:
    """ "Log in with Strava", done by Authlib (state/CSRF check and code exchange included).

    Kept behind this small class so tests can swap in a fake instead of calling Strava.
    """

    def __init__(self, config: StravaConfig):
        self.oauth = OAuth()
        self.oauth.register(
            name="strava",
            client_id=config.client_id,
            client_secret=config.client_secret,
            authorize_url=AUTHORIZE_URL,
            access_token_url=TOKEN_URL,
            client_kwargs={"scope": SCOPE, "token_endpoint_auth_method": "client_secret_post"},
        )

    async def redirect(self, request: Request, callback_url: str) -> RedirectResponse:
        return await self.oauth.strava.authorize_redirect(
            request, callback_url, approval_prompt="auto"
        )

    async def finish(self, request: Request) -> tuple[dict, Tokens] | str:
        """The Strava athlete and their tokens, or why login failed: "denied" or "scope"."""
        if request.query_params.get("error"):
            return "denied"
        if REQUIRED_SCOPE not in request.query_params.get("scope", ""):
            return "scope"
        token = await self.oauth.strava.authorize_access_token(request)
        tokens = Tokens(token["access_token"], token["refresh_token"], token["expires_at"])
        return token["athlete"], tokens
