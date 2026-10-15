import httpx

from stridecraft.config import StravaConfig
from stridecraft.strava.auth import StravaAuth, Tokens, TokenStore
from stridecraft.strava.client import API_URL, StravaClient


def make_client(tmp_path, requested):
    def handler(request):
        requested.append(request.url.path)
        if request.url.path.endswith("/athlete/activities"):
            return httpx.Response(
                200,
                json=[
                    {"id": 1, "sport_type": "Run", "trainer": False},
                    {"id": 2, "sport_type": "Run", "trainer": True},
                    {"id": 3, "sport_type": "Ride", "trainer": False},
                ],
            )
        return httpx.Response(200, json={"id": 1, "best_efforts": []})

    store = TokenStore(tmp_path / "tokens.json")
    store.save(Tokens("tok", "r", 9999999999))
    auth = StravaAuth(StravaConfig("id", "secret"), store)
    http = httpx.Client(base_url=API_URL, transport=httpx.MockTransport(handler))
    return StravaClient(auth, http)


def test_detail_fetched_for_gps_runs_only_and_non_runs_ignored(tmp_path):
    requested = []
    activities = make_client(tmp_path, requested).fetch_activities(after_epoch=0)

    assert [a["id"] for a in activities] == [1, 2]
    detail_calls = [p for p in requested if "/activities/" in p]
    assert detail_calls == ["/api/v3/activities/1"]


def test_already_stored_runs_cost_no_detail_call(tmp_path):
    requested = []
    activities = make_client(tmp_path, requested).fetch_activities(after_epoch=0, skip_ids={"1"})

    assert [a["id"] for a in activities] == [2]
    assert not [p for p in requested if "/activities/" in p]
