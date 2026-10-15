from datetime import UTC, datetime

from sqlalchemy.orm import Session

from stridecraft.content.registry import Content
from stridecraft.db.repositories import StriderRepository
from stridecraft.errors import AdoptionError
from stridecraft.models import Strider, User
from stridecraft.utils.names import clean_name


class AdoptionService:
    """Picking a breed and a name creates the strider. Its `adopted_at` is the sign-up date."""

    def __init__(self, session: Session, content: Content):
        self.striders = StriderRepository(session)
        self.content = content

    def adopt(
        self, user: User, breed: str, name: str, adopted_at: datetime | None = None
    ) -> Strider:
        if breed not in self.content.breeds:
            known = ", ".join(sorted(self.content.breeds)) or "none yet"
            raise AdoptionError(f"Unknown breed {breed!r} (available: {known})")
        if self.striders.get_for_user(user.id):
            raise AdoptionError("This user already has a strider")
        try:
            name = clean_name(name)
        except ValueError as error:
            raise AdoptionError(str(error)) from error
        return self.striders.create(user.id, breed, name, adopted_at or datetime.now(UTC))
