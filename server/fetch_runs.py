"""Fetch recent Strava runs: authorizes on first use, dumps raw JSON, prints a summary."""

import json
import time
from datetime import UTC, datetime
from pathlib import Path

from stridecraft.config import STATS_WINDOW_DAYS, StravaConfig
from stridecraft.models import Run
from stridecraft.stats.stats_calculator import StatConverter
from stridecraft.strava.auth import StravaAuth, TokenStore
from stridecraft.strava.client import StravaClient

ROOT = Path(__file__).parent
RAW_DIR = ROOT / "data" / "raw"
SECONDS_PER_DAY = 86400


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
        f"{'training' if run.is_training else 'easy    '}  PRs: {', '.join(prs) or '-'}"
    )


def print_stats(runs: list[Run], signup_date: datetime) -> None:
    stats = StatConverter().convert(runs, signup_date).stats
    print(f"\nPal stats for runs since {signup_date:%Y-%m-%d} (base 10):")
    print(f"  Speed {stats.speed:.3f}  Endurance {stats.endurance:.3f}")
    print(f"  Hills {stats.hills:.3f}  Consistency {stats.consistency:.3f}")


def main(signup_date: datetime | None = None) -> None:
    """`signup_date` defaults to now, so no run counts yet; pass an earlier date to try stats."""
    signup_date = signup_date or datetime.now(UTC)
    auth = StravaAuth(StravaConfig.from_env(), TokenStore(ROOT / "tokens.json"))
    auth.ensure_authorized()
    client = StravaClient(auth)

    after = int(time.time()) - STATS_WINDOW_DAYS * SECONDS_PER_DAY
    details = client.fetch_activities(after)
    print(f"{len(details)} runs in the last {STATS_WINDOW_DAYS} days")
    dump_raw(details)

    user_id = client.athlete_id()
    runs = [Run.from_strava(detail, user_id) for detail in details]
    for run in sorted(runs, key=lambda r: r.start_time):
        print_run(run)
    print_stats(runs, signup_date)


if __name__ == "__main__":
    main()
