import time
from datetime import UTC, datetime, timedelta

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from sqlalchemy import text

from stridecraft.api.app import create_app
from stridecraft.config import AppConfig, StravaConfig
from stridecraft.content.models import Breed
from stridecraft.db.database import IN_MEMORY_URL, Database
from stridecraft.errors import NotAuthorizedError
from stridecraft.strava.auth import Tokens
from stridecraft.strava.client import RunListing

FRONTEND = "http://frontend.test"


class FakeLogin:
    """Stands in for "log in with Strava": the next login is whichever athlete is set."""

    def __init__(self):
        self.athlete = {"id": 111, "username": "ada", "firstname": "Ada", "profile": "http://p"}
        self.failure: str | None = None

    async def redirect(self, request, callback_url):
        raise NotImplementedError

    async def finish(self, request):
        if self.failure:
            return self.failure
        return self.athlete, Tokens("access-secret", "refresh-secret", int(time.time()) + 3600)


@pytest.fixture
def login():
    return FakeLogin()


def build_app(login, **config_overrides):
    config = AppConfig(
        "s" * 32, Fernet.generate_key().decode(), FRONTEND, "http://api.test", **config_overrides
    )
    return create_app(config, StravaConfig("id", "secret"), Database(IN_MEMORY_URL), login)


@pytest.fixture
def app(login):
    return build_app(login)


@pytest.fixture
def client(app):
    with TestClient(app, base_url="http://api.test", follow_redirects=False) as client:
        yield client


def log_in(client, login, athlete_id=111):
    login.athlete = {**login.athlete, "id": athlete_id}
    response = client.get("/auth/strava/callback")
    assert response.status_code == 302
    return response


def adopt(client, name="Aura", breed="cetus"):
    return client.post("/me/strider", json={"breed": breed, "name": name})


class FakeImporter:
    """An import that finds one run at adoption, or fails like Strava would."""

    def __init__(self, app):
        self.app = app
        self.error: Exception | None = None
        self.calls: list[int] = []

    def import_for(self, user_id):
        from stridecraft.services.importer import Importer

        self.calls.append(user_id)
        if self.error:
            raise self.error
        state = self.app.state.stridecraft
        activity = {
            "id": 1,
            "sport_type": "Run",
            "start_date": (datetime.now(UTC) + timedelta(seconds=1)).isoformat(),
            "distance": 10000.0,
            "moving_time": 3000,
            "total_elevation_gain": 100.0,
            "workout_type": 0,
        }
        fake_client = type(
            "C",
            (),
            {
                "new_summaries": lambda self, *a, **k: RunListing([activity], False),
                "activity_detail": lambda self, i: activity,
            },
        )()
        importer = Importer(state.database, None, state.cipher)
        importer.client_for = lambda uid: fake_client
        return importer.import_for(user_id)


@pytest.fixture
def importer(app):
    fake = FakeImporter(app)
    app.state.stridecraft.importer = fake
    return fake


def test_the_api_needs_a_login(client):
    assert client.get("/me").status_code == 401
    assert client.post("/me/strider", json={"breed": "cetus", "name": "x"}).status_code == 401
    assert client.get("/me/sync").status_code == 401


def test_a_new_user_is_created_at_login_and_has_no_strider_yet(client, login):
    response = log_in(client, login)
    assert response.headers["location"] == FRONTEND

    me = client.get("/me").json()
    assert me["firstname"] == "Ada"
    assert me["strider"] is None


def test_logging_in_again_is_the_same_user_with_a_fresh_profile(client, login):
    log_in(client, login)
    first = client.get("/me").json()["id"]
    client.post("/auth/logout")
    assert client.get("/me").status_code == 401

    login.athlete = {**login.athlete, "firstname": "Ada L."}
    log_in(client, login)
    me = client.get("/me").json()
    assert me["id"] == first
    assert me["firstname"] == "Ada L."


@pytest.mark.parametrize("failure", ["denied", "scope"])
def test_a_failed_strava_login_goes_back_to_the_frontend_with_the_reason(client, login, failure):
    login.failure = failure
    response = client.get("/auth/strava/callback")
    assert response.headers["location"] == f"{FRONTEND}?error={failure}"
    assert client.get("/me").status_code == 401


def test_strava_tokens_are_not_stored_in_plain_text(app, client, login):
    log_in(client, login)
    with app.state.stridecraft.database.engine.connect() as connection:
        stored = connection.execute(text("select access_token, refresh_token from strava_tokens"))
        row = stored.one()
    assert "access-secret" not in row[0] and "refresh-secret" not in row[1]


def test_adopting_creates_the_strider_once(client, login, importer):
    log_in(client, login)

    first = adopt(client)
    assert first.status_code == 201
    assert first.json()["stats"]["speed"] == 10.0
    assert client.get("/me").json()["strider"]["name"] == "Aura"

    again = adopt(client, name="Other")
    assert again.status_code == 409
    assert again.json()["code"] == "already_adopted"


@pytest.mark.parametrize(
    "body", [{"breed": "nope", "name": "Aura"}, {"breed": "cetus", "name": " "}]
)
def test_unusable_adoptions_are_rejected_with_a_message(client, login, importer, body):
    log_in(client, login)
    response = client.post("/me/strider", json=body)
    assert response.status_code == 422
    assert response.json()["code"] == "invalid_adoption"
    assert client.get("/me").json()["strider"] is None


def test_adopting_imports_runs_in_the_background_and_stats_grow(client, login, importer):
    log_in(client, login)
    adopt(client)

    sync = client.get("/me/sync").json()
    assert sync["state"] == "idle"
    assert sync["last_result"]["new_runs"] == 1
    assert sync["last_synced_at"] is not None
    assert client.get("/me/strider").json()["stats"]["endurance"] > 10.0


def test_a_failed_import_is_reported_not_crashed(client, login, importer):
    importer.error = NotAuthorizedError("Strava no longer accepts the saved login; connect again")
    log_in(client, login)
    assert adopt(client).status_code == 201

    sync = client.get("/me/sync").json()
    assert sync["state"] == "failed"
    assert "connect again" in sync["error"]


def test_syncing_needs_a_strider_and_cannot_overlap(app, client, login, importer):
    log_in(client, login)
    assert client.post("/me/sync").json()["code"] == "no_strider"

    adopt(client)
    user_id = client.get("/me").json()["id"]
    app.state.stridecraft.jobs.start(user_id)  # an import is still going
    response = client.post("/me/sync")
    assert response.status_code == 409
    assert response.json()["code"] == "sync_in_progress"


def test_starting_over_is_a_dev_tool_that_is_off_by_default(client, login, importer):
    log_in(client, login)
    adopt(client)
    assert client.delete("/me/strider").status_code == 405  # the route is not registered


@pytest.fixture
def dev_client(login):
    app = build_app(login, dev_tools=True)
    app.state.stridecraft.importer = FakeImporter(app)
    with TestClient(app, base_url="http://api.test", follow_redirects=False) as client:
        client.app_state = app.state.stridecraft
        yield client


def test_starting_over_removes_the_strider_and_runs_but_keeps_the_login(dev_client, login):
    log_in(dev_client, login)
    assert dev_client.delete("/me/strider").json()["code"] == "no_strider"

    adopt(dev_client)
    assert dev_client.delete("/me/strider").status_code == 204
    me = dev_client.get("/me")
    assert me.status_code == 200
    assert me.json()["strider"] is None
    assert dev_client.get("/me/sync").json()["last_synced_at"] is None

    assert adopt(dev_client, name="Again").status_code == 201
    assert dev_client.get("/me/sync").json()["last_result"]["new_runs"] == 1


def test_starting_over_waits_for_a_running_import(dev_client, login):
    log_in(dev_client, login)
    adopt(dev_client)
    dev_client.app_state.jobs.start(dev_client.get("/me").json()["id"])
    assert dev_client.delete("/me/strider").status_code == 409
    assert dev_client.get("/me").json()["strider"] is not None


def test_two_users_never_see_each_others_striders(client, login, importer):
    log_in(client, login, athlete_id=111)
    adopt(client, name="Ada's")
    client.post("/auth/logout")

    log_in(client, login, athlete_id=222)
    assert client.get("/me").json()["strider"] is None
    assert client.get("/me/strider").status_code == 404
    adopt(client, name="Bea's")
    assert client.get("/me/strider").json()["name"] == "Bea's"
    assert importer.calls[0] != importer.calls[1]


def test_breeds_and_a_suggested_name_are_public(client):
    assert any(b["id"] == "cetus" for b in client.get("/breeds").json())
    assert client.get("/names/random").json()["name"]


def test_breed_model_urls_come_from_the_asset_base(app, client):
    app.state.stridecraft.content.breeds["modelled"] = Breed(
        id="modelled", name="M", description="d", model="breeds/modelled.glb"
    )
    breeds = {b["id"]: b for b in client.get("/breeds").json()}
    assert breeds["cetus"]["model_url"] is None
    assert breeds["modelled"]["model_url"] == "http://api.test/assets/breeds/modelled.glb"


def test_the_openapi_spec_builds_with_clean_operation_ids(app):
    spec = app.openapi()
    assert spec["paths"]["/me"]["get"]["operationId"] == "get_me"
    assert "/me/strider" in spec["paths"]
