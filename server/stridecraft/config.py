import os
from dataclasses import dataclass
from pathlib import Path

# Game content definitions (YAML, one file per entity); see journal/0008.
CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"

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
