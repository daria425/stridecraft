import time
from dataclasses import dataclass

import httpx

from stridecraft.errors import NotAuthorizedError, RateLimitError, StravaError
from stridecraft.models import RUN_SPORT_TYPES
from stridecraft.strava.auth import StravaAuth

API_URL = "https://www.strava.com/api/v3"
PAGE_SIZE = 200
# Strava does not document the order activities come back in, so we never rely on it: listing
# goes through fixed time windows (before/after), newest window first, and sorts for itself.
WINDOW_SECONDS = 90 * 86400
# One list request per page, so this bounds the requests (and memory) of any single sync however
# long the user was away. Past it the oldest windows are left out, never a partial window.
MAX_LIST_PAGES = 25


@dataclass(frozen=True)
class RunListing:
    summaries: list[dict]
    truncated: bool  # True if older runs were left out because of MAX_LIST_PAGES


class StravaClient:
    def __init__(self, auth: StravaAuth, http: httpx.Client | None = None):
        self.auth = auth
        self.http = http or httpx.Client(base_url=API_URL, timeout=30)

    def get(self, path: str, params: dict | None = None):
        try:
            response = self.http.get(
                path,
                params=params,
                headers={"Authorization": f"Bearer {self.auth.valid_access_token()}"},
            )
        except httpx.TransportError as error:
            raise StravaError("Could not reach Strava") from error
        if response.status_code == 429:
            usage = response.headers.get("X-RateLimit-Usage", "unknown")
            raise RateLimitError(f"Strava is limiting requests (15min,daily usage: {usage})")
        if response.status_code == 401:
            raise NotAuthorizedError("Strava rejected our access; connect again")
        if response.is_error:
            raise StravaError(f"Strava returned an error ({response.status_code})")
        return response.json()

    def athlete(self) -> dict:
        return self.get("/athlete")

    def athlete_id(self) -> int:
        return self.athlete()["id"]

    def list_run_summaries(self, after_epoch: int, before_epoch: int) -> RunListing:
        """Runs that started in [after_epoch, before_epoch), newest 90-day window first."""
        runs: dict[int, dict] = {}  # by id: a boundary run may be returned by two windows
        pages_left = MAX_LIST_PAGES
        end = before_epoch
        while end > after_epoch:
            start = max(after_epoch, end - WINDOW_SECONDS)
            window = self.list_window(start, end, pages_left)
            if window is None:
                return RunListing(list(runs.values()), truncated=True)
            found, pages_used = window
            runs.update({run["id"]: run for run in found})
            pages_left -= pages_used
            end = start
        return RunListing(list(runs.values()), truncated=False)

    def list_window(self, start: int, end: int, max_pages: int) -> tuple[list[dict], int] | None:
        """Every run in the window and the pages it took, or None if `max_pages` is not enough
        (a half-listed window is an arbitrary subset, so it is dropped entirely)."""
        runs: list[dict] = []
        for page in range(1, max_pages + 1):
            batch = self.get(
                "/athlete/activities",
                # `after` is exclusive, hence start - 1, so a run starting exactly at `start` counts
                {"after": start - 1, "before": end, "per_page": PAGE_SIZE, "page": page},
            )
            runs += [a for a in batch if a.get("sport_type") in RUN_SPORT_TYPES]
            if len(batch) < PAGE_SIZE:
                return runs, page
        return None

    def activity_detail(self, activity_id: int) -> dict:
        """Full activity, including best_efforts (one API call each)."""
        return self.get(f"/activities/{activity_id}")

    def new_summaries(
        self,
        after_epoch: int,
        skip_ids: frozenset[str] | set[str] = frozenset(),
        before_epoch: int | None = None,
    ) -> RunListing:
        """Run summaries since `after_epoch` whose id is not in `skip_ids` (already stored)."""
        listing = self.list_run_summaries(after_epoch, before_epoch or int(time.time()) + 1)
        wanted = [s for s in listing.summaries if str(s["id"]) not in skip_ids]
        return RunListing(wanted, listing.truncated)

    def run_detail(self, summary: dict) -> dict:
        """Full activity for GPS runs; treadmill has no best efforts, so no call."""
        return summary if summary.get("trainer") else self.activity_detail(summary["id"])

    def fetch_activities(self, after_epoch: int) -> list[dict]:
        """Every detail at once, for the dump script. Sync does not: see DETAIL_CAP there."""
        return [self.run_detail(s) for s in self.new_summaries(after_epoch).summaries]
