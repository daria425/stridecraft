import time

import httpx
import pytest

from stridecraft.config import StravaConfig
from stridecraft.errors import NotAuthorizedError, RateLimitError, StravaError
from stridecraft.strava.auth import StravaAuth, Tokens, TokenStore
from stridecraft.strava.client import API_URL, WINDOW_SECONDS, StravaClient

NOW = int(time.time())
DAY = 86400


def make_client(tmp_path, handler):
    store = TokenStore(tmp_path / "tokens.json")
    store.save(Tokens("tok", "r", 9999999999))
    auth = StravaAuth(StravaConfig("id", "secret"), store)
    http = httpx.Client(base_url=API_URL, transport=httpx.MockTransport(handler))
    return StravaClient(auth, http)


def strava_listing(activities, inclusive=False):
    """A handler that filters `activities` (id, start epoch) by before/after like Strava, with
    either strict or inclusive bounds (its docs don't say which), and pages them."""

    def handler(request):
        if not request.url.path.endswith("/athlete/activities"):
            return httpx.Response(200, json={"id": 1, "best_efforts": []})
        query = request.url.params
        after, before = int(query["after"]), int(query["before"])
        page, size = int(query["page"]), int(query["per_page"])
        keep = (lambda t: after <= t <= before) if inclusive else (lambda t: after < t < before)
        found = [
            {"id": id, "sport_type": "Run", "trainer": False}
            for id, start in activities
            if keep(start)
        ]
        return httpx.Response(200, json=found[(page - 1) * size : page * size])

    return handler


def test_detail_fetched_for_gps_runs_only_and_non_runs_ignored(tmp_path):
    requested = []

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

    activities = make_client(tmp_path, handler).fetch_activities(after_epoch=NOW - DAY)

    assert [a["id"] for a in activities] == [1, 2]
    assert [p for p in requested if "/activities/" in p] == ["/api/v3/activities/1"]


@pytest.mark.parametrize("inclusive", [False, True])
def test_a_long_absence_is_listed_across_windows_without_gaps_or_duplicates(tmp_path, inclusive):
    # Runs spread over ~300 days, including ones exactly on a window edge.
    edge = NOW - WINDOW_SECONDS
    runs = [(1, NOW - 5 * DAY), (2, edge), (3, edge - 1), (4, edge + 1), (5, NOW - 250 * DAY)]
    client = make_client(tmp_path, strava_listing(runs, inclusive))

    listing = client.new_summaries(after_epoch=NOW - 300 * DAY, before_epoch=NOW)

    assert sorted(s["id"] for s in listing.summaries) == [1, 2, 3, 4, 5]
    assert not listing.truncated


def test_when_the_page_budget_runs_out_whole_old_windows_are_dropped_not_half_listed(
    tmp_path, monkeypatch
):
    monkeypatch.setattr("stridecraft.strava.client.PAGE_SIZE", 2)
    monkeypatch.setattr("stridecraft.strava.client.MAX_LIST_PAGES", 3)
    window = WINDOW_SECONDS
    # Two runs in each of the 3 newest windows; each window costs 2 pages (a full page, then an
    # empty one to know it is the end), so only the newest window fits in 3 pages.
    runs = [(10, NOW - 1000), (11, NOW - 2000)]
    runs += [(20, NOW - window - 1000), (21, NOW - window - 2000)]
    runs += [(30, NOW - 2 * window - 1000), (31, NOW - 2 * window - 2000)]
    client = make_client(tmp_path, strava_listing(runs))

    listing = client.new_summaries(after_epoch=NOW - 3 * window, before_epoch=NOW)

    assert sorted(s["id"] for s in listing.summaries) == [10, 11]
    assert listing.truncated


def test_stored_runs_are_dropped_from_the_listing_so_they_cost_no_detail_call(tmp_path):
    client = make_client(tmp_path, strava_listing([(1, NOW - DAY), (2, NOW - 2 * DAY)]))

    listing = client.new_summaries(NOW - 10 * DAY, skip_ids={"1"}, before_epoch=NOW)

    assert [s["id"] for s in listing.summaries] == [2]


@pytest.mark.parametrize(
    "status, error",
    [(401, NotAuthorizedError), (429, RateLimitError), (500, StravaError), (503, StravaError)],
)
def test_strava_failures_become_errors_a_caller_can_handle(tmp_path, status, error):
    client = make_client(tmp_path, lambda request: httpx.Response(status))
    with pytest.raises(error):
        client.athlete()


def test_cannot_reach_strava_is_a_strava_error(tmp_path):
    def unreachable(request):
        raise httpx.ConnectError("no network")

    with pytest.raises(StravaError):
        make_client(tmp_path, unreachable).athlete()
