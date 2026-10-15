import pytest

from stridecraft.content.registry import Content
from stridecraft.db.database import IN_MEMORY_URL, Database
from stridecraft.db.repositories import UserRepository


@pytest.fixture
def session():
    with Database(IN_MEMORY_URL).session() as session:
        yield session


@pytest.fixture
def user(session):
    user = UserRepository(session).create(strava_athlete_id=555, username="runner")
    session.commit()
    return user


@pytest.fixture(scope="session")
def content():
    return Content.load()
