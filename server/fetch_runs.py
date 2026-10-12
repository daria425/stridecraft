"""Fetch recent Strava runs: authorizes on first use, dumps raw JSON, prints a summary."""

import json
import time
from pathlib import Path

from stridecraft.config import STATS_WINDOW_DAYS, StravaConfig
from stridecraft.models import Run
from stridecraft.strava.auth import StravaAuth, TokenStore
from stridecraft.strava.client import StravaClient

ROOT = Path(__file__).parent
RAW_DIR = ROOT / "data" / "raw"
SECONDS_PER_DAY = 86400


def ensure_authorized(auth: StravaAuth) -> None:
    if auth.store.load() is not None:
        return
    print(f"Open this URL and approve access:\n\n{auth.authorize_url()}\n")
    print("You'll land on a broken localhost page; copy the `code=` value from its URL.")
    auth.exchange_code(input("code: ").strip())


def dump_raw(details: list[dict]) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for detail in details:
        (RAW_DIR / f"{detail['id']}.json").write_text(json.dumps(detail, indent=2))


def print_run(run: Run) -> None:
    pace = run.moving_time_s / (run.distance_m / 1000) if run.distance_m else 0
    prs = [e.name for e in run.best_efforts if e.pr_rank == 1]
    print(
        f"{run.start_time:%Y-%m-%d}  {run.distance_m / 1000:6.2f} km  "
        f"{int(pace // 60)}:{int(pace % 60):02d}/km  +{run.elevation_gain_m:4.0f} m  "
        f"{'training' if run.training_default else 'easy    '}  PRs: {', '.join(prs) or '-'}"
    )


def main() -> None:
    auth = StravaAuth(StravaConfig.from_env(), TokenStore(ROOT / "tokens.json"))
    ensure_authorized(auth)
    client = StravaClient(auth)

    after = int(time.time()) - STATS_WINDOW_DAYS * SECONDS_PER_DAY
    details = client.fetch_activities(after)
    print(f"{len(details)} runs in the last {STATS_WINDOW_DAYS} days")
    dump_raw(details)

    user_id = client.athlete_id()
    for detail in sorted(details, key=lambda d: d["start_date"]):
        print_run(Run.from_strava(detail, user_id))


if __name__ == "__main__":
    main()
