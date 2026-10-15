import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlencode

import httpx

from stridecraft.config import StravaConfig
from stridecraft.errors import NotAuthorizedError, StravaError

AUTHORIZE_URL = "https://www.strava.com/oauth/authorize"
TOKEN_URL = "https://www.strava.com/oauth/token"
REDIRECT_URI = "http://localhost"
SCOPE = "activity:read_all"
EXPIRY_MARGIN_S = 60


@dataclass
class Tokens:
    access_token: str
    refresh_token: str
    expires_at: int

    def is_expired(self) -> bool:
        return self.expires_at - EXPIRY_MARGIN_S <= time.time()


class TokenStore:
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> Tokens | None:
        if not self.path.exists():
            return None
        return Tokens(**json.loads(self.path.read_text()))

    def save(self, tokens: Tokens) -> None:
        self.path.write_text(json.dumps(asdict(tokens)))


class StravaAuth:
    def __init__(self, config: StravaConfig, store: TokenStore, http: httpx.Client | None = None):
        self.config = config
        self.store = store
        self.http = http or httpx.Client()

    def authorize_url(self) -> str:
        query = urlencode(
            {
                "client_id": self.config.client_id,
                "redirect_uri": REDIRECT_URI,
                "response_type": "code",
                "approval_prompt": "auto",
                "scope": SCOPE,
            }
        )
        return f"{AUTHORIZE_URL}?{query}"

    def ensure_authorized(self) -> None:
        """First run only: walk the user through approving access and paste back the code."""
        if self.store.load() is not None:
            return
        print(f"Open this URL and approve access:\n\n{self.authorize_url()}\n")
        print("You'll land on a broken localhost page; copy the `code=` value from its URL.")
        self.exchange_code(input("code: ").strip())

    def exchange_code(self, code: str) -> Tokens:
        return self.request_tokens({"grant_type": "authorization_code", "code": code})

    def valid_access_token(self) -> str:
        tokens = self.store.load()
        if tokens is None:
            raise NotAuthorizedError("Strava access has not been set up yet")
        if tokens.is_expired():
            tokens = self.request_tokens(
                {"grant_type": "refresh_token", "refresh_token": tokens.refresh_token}
            )
        return tokens.access_token

    def request_tokens(self, grant: dict) -> Tokens:
        response = self.http.post(
            TOKEN_URL,
            data={
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                **grant,
            },
        )
        if response.status_code in (400, 401):
            raise NotAuthorizedError("Strava no longer accepts the saved login; connect again")
        if response.is_error:
            raise StravaError(f"Strava returned an error while logging in ({response.status_code})")
        body = response.json()
        # Strava may rotate the refresh token, so always persist the latest pair.
        tokens = Tokens(body["access_token"], body["refresh_token"], body["expires_at"])
        self.store.save(tokens)
        return tokens
