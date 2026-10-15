import os
from dataclasses import dataclass
from pathlib import Path

# Game content definitions (YAML, one file per entity); see journal/0008.
CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"

# Where the SQLite database lives (data/ is gitignored); see journal/0006.
DATABASE_PATH = Path(__file__).resolve().parent.parent / "data" / "stridecraft.db"

# Strava OAuth tokens (gitignored); see journal/0006 on why they stay in a file for now.
TOKENS_PATH = Path(__file__).resolve().parent.parent / "tokens.json"

# Source of default strider names (a plain list under the "names" key).
NAMES_PATH = Path(__file__).resolve().parent.parent / "static" / "names_src.json"

# Rolling stats window; tune later (see CLAUDE.md "Stats").
STATS_WINDOW_DAYS = 42


@dataclass(frozen=True)
class StravaConfig:
    client_id: str
    client_secret: str

    @classmethod
    def from_env(cls) -> "StravaConfig":
        try:
            return cls(os.environ["STRAVA_CLIENT_ID"], os.environ["STRAVA_CLIENT_SECRET"])
        except KeyError as missing:
            raise SystemExit(
                f"Missing {missing} - copy .env.example to .env "
                "and run with `uv run --env-file .env`"
            ) from None


@dataclass(frozen=True)
class AppConfig:
    """Settings for the web API (the CLI does not need them)."""

    session_secret: str  # signs the login cookie
    token_encryption_key: str  # Fernet key; encrypts Strava tokens in the database
    frontend_url: str  # where the browser is sent after login, and the allowed CORS origin
    public_url: str  # where this API is reachable by the browser (Strava redirects back to it)

    @classmethod
    def from_env(cls) -> "AppConfig":
        try:
            return cls(
                os.environ["SESSION_SECRET"],
                os.environ["TOKEN_ENCRYPTION_KEY"],
                os.environ.get("FRONTEND_URL", "http://localhost:5173"),
                os.environ.get("PUBLIC_URL", "http://localhost:8000"),
            )
        except KeyError as missing:
            raise SystemExit(f"Missing {missing} - see .env.example") from None
