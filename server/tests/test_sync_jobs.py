import threading

import pytest
from cryptography.fernet import Fernet

from stridecraft.db.database import IN_MEMORY_URL, Database
from stridecraft.db.repositories import StriderRepository, UserRepository
from stridecraft.errors import AlreadyAdoptedError, NotAuthorizedError, SyncInProgressError
from stridecraft.services.sync import SyncResult
from stridecraft.services.sync_jobs import SyncJobs, SyncState
from stridecraft.strava.auth import Tokens
from stridecraft.strava.db_tokens import DbTokenStore


def test_a_second_import_for_the_same_user_is_refused_until_the_first_ends():
    jobs = SyncJobs()
    jobs.start(1)
    with pytest.raises(SyncInProgressError):
        jobs.start(1)

    jobs.start(2)  # another user is independent
    jobs.run(1, lambda: SyncResult(3, 0, 0))
    assert jobs.status(1).state is SyncState.IDLE
    assert jobs.status(1).result.new_runs == 3
    jobs.start(1)  # free again


def test_a_failed_import_keeps_the_last_good_result_and_says_why():
    jobs = SyncJobs()
    jobs.start(1)
    jobs.run(1, lambda: SyncResult(3, 0, 0))
    jobs.start(1)

    def revoked():
        raise NotAuthorizedError("connect again")

    jobs.run(1, revoked)
    status = jobs.status(1)
    assert status.state is SyncState.FAILED
    assert status.error == "connect again"
    assert status.result.new_runs == 3


def test_imports_for_different_users_never_overlap_because_strava_limits_the_app():
    jobs = SyncJobs()
    jobs.start(1)
    jobs.start(2)
    inside = []
    overlaps = []

    def slow_import():
        inside.append(1)
        overlaps.append(len(inside) > 1)
        threading.Event().wait(0.05)
        inside.pop()
        return SyncResult(0, 0, 0)

    threads = [threading.Thread(target=jobs.run, args=(uid, slow_import)) for uid in (1, 2)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert not any(overlaps)


def test_the_same_strava_athlete_logging_in_twice_is_one_user(session):
    users = UserRepository(session)
    first = users.upsert_profile(7, "a", "A", None)
    again = users.upsert_profile(7, "a2", "A2", None)
    assert again.id == first.id
    assert users.get(first.id).firstname == "A2"


def test_a_double_adoption_is_a_typed_error_not_a_database_crash(session, user):
    striders = StriderRepository(session)
    from datetime import UTC, datetime

    striders.create(user.id, "cetus", "One", datetime.now(UTC), 50)
    with pytest.raises(AlreadyAdoptedError):
        striders.create(user.id, "cetus", "Two", datetime.now(UTC), 50)


def test_each_users_tokens_are_kept_apart_and_unreadable_with_another_key():
    database = Database(IN_MEMORY_URL)
    with database.session() as session:
        users = UserRepository(session)
        a, b = users.create(1).id, users.create(2).id
        session.commit()
    cipher = Fernet(Fernet.generate_key())
    store_a, store_b = DbTokenStore(database, cipher, a), DbTokenStore(database, cipher, b)

    assert store_a.load() is None
    store_a.save(Tokens("a-access", "a-refresh", 10))
    store_b.save(Tokens("b-access", "b-refresh", 20))
    assert store_a.load() == Tokens("a-access", "a-refresh", 10)
    assert store_b.load().access_token == "b-access"

    with pytest.raises(Exception):  # noqa: B017 - cryptography's InvalidToken
        DbTokenStore(database, Fernet(Fernet.generate_key()), a).load()
