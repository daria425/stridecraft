from sqlalchemy.orm import Session

from stridecraft.db.repositories import RunRepository, StriderRepository, UserRepository
from stridecraft.errors import NoStriderError
from stridecraft.models import User


class StriderReset:
    """Dev tool: take a user back to before adoption. The user and their Strava login stay; the
    strider, every stored run and the sync time go, so the next adoption imports from scratch."""

    def __init__(self, session: Session):
        self.session = session

    def reset(self, user: User) -> None:
        striders = StriderRepository(self.session)
        if striders.get_for_user(user.id) is None:
            raise NoStriderError("There is no strider to remove")
        RunRepository(self.session).delete_all(user.id)
        striders.delete_for_user(user.id)
        UserRepository(self.session).clear_synced(user.id)
