import httpx

from stridecraft.models import RUN_SPORT_TYPES
from stridecraft.strava.auth import StravaAuth

API_URL = "https://www.strava.com/api/v3"
PAGE_SIZE = 200


class RateLimitError(RuntimeError):
    pass


class StravaClient:
    def __init__(self, auth: StravaAuth, http: httpx.Client | None = None):
        self.auth = auth
        self.http = http or httpx.Client(base_url=API_URL, timeout=30)

    def get(self, path: str, params: dict | None = None):
        response = self.http.get(
            path,
            params=params,
            headers={"Authorization": f"Bearer {self.auth.valid_access_token()}"},
        )
        if response.status_code == 429:
            usage = response.headers.get("X-RateLimit-Usage", "unknown")
            raise RateLimitError(f"Strava rate limit hit (15min,daily usage: {usage})")
        response.raise_for_status()
        return response.json()

    def athlete_id(self) -> int:
        return self.get("/athlete")["id"]

    def list_run_summaries(self, after_epoch: int) -> list[dict]:
        """Raw activity summaries for runs since `after_epoch`, across all pages."""
        runs: list[dict] = []
        page = 1
        while True:
            batch = self.get(
                "/athlete/activities",
                {"after": after_epoch, "per_page": PAGE_SIZE, "page": page},
            )
            runs += [a for a in batch if a.get("sport_type") in RUN_SPORT_TYPES]
            if len(batch) < PAGE_SIZE:
                return runs
            page += 1

    def activity_detail(self, activity_id: int) -> dict:
        """Full activity, including best_efforts (one API call each)."""
        return self.get(f"/activities/{activity_id}")

    def fetch_activities(self, after_epoch: int) -> list[dict]:
        """Runs since `after_epoch`; detail only for GPS runs, as treadmill has no efforts."""
        return [
            summary if summary.get("trainer") else self.activity_detail(summary["id"])
            for summary in self.list_run_summaries(after_epoch)
        ]
