import time

import httpx
import pytest

from stridecraft.config import StravaConfig
from stridecraft.errors import NotAuthorizedError
from stridecraft.strava.auth import StravaAuth, Tokens, TokenStore


def make_auth(tmp_path, handler):
    http = httpx.Client(transport=httpx.MockTransport(handler))
    store = TokenStore(tmp_path / "tokens.json")
    return StravaAuth(StravaConfig("id", "secret"), store, http), store


def test_fresh_token_is_reused_without_network(tmp_path):
    def no_calls(request):
        raise AssertionError("should not hit the network")

    auth, store = make_auth(tmp_path, no_calls)
    store.save(Tokens("live", "r", int(time.time()) + 3600))
    assert auth.valid_access_token() == "live"


def test_expired_token_is_refreshed_and_rotated_refresh_token_saved(tmp_path):
    def refresh(request):
        assert b"grant_type=refresh_token" in request.content
        assert b"refresh_token=old-refresh" in request.content
        return httpx.Response(
            200,
            json={
                "access_token": "new",
                "refresh_token": "rotated-refresh",
                "expires_at": int(time.time()) + 3600,
            },
        )

    auth, store = make_auth(tmp_path, refresh)
    store.save(Tokens("stale", "old-refresh", int(time.time()) - 10))
    assert auth.valid_access_token() == "new"
    assert store.load().refresh_token == "rotated-refresh"


def test_token_inside_expiry_margin_counts_as_expired():
    assert Tokens("a", "r", int(time.time()) + 30).is_expired()


def test_missing_tokens_mean_not_authorized(tmp_path):
    auth, _ = make_auth(tmp_path, lambda r: httpx.Response(500))
    with pytest.raises(NotAuthorizedError):
        auth.valid_access_token()


def test_a_refresh_token_strava_rejects_means_connect_again(tmp_path):
    """E.g. someone returns after years, or revoked access in Strava's settings."""
    auth, store = make_auth(tmp_path, lambda r: httpx.Response(400))
    store.save(Tokens("stale", "dead-refresh", int(time.time()) - 10))
    with pytest.raises(NotAuthorizedError):
        auth.valid_access_token()
