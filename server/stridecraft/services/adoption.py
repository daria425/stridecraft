from datetime import UTC, datetime

from sqlalchemy.orm import Session

from stridecraft.content.registry import Content
from stridecraft.db.repositories import StriderRepository
from stridecraft.errors import AdoptionError, AlreadyAdoptedError
from stridecraft.models import Strider, User
from stridecraft.utils.names import clean_name, random_name

# Kilometres between waypoints on the journey: smaller means faster progression through the
# same story. Keep the bounds in step with the adoption page in web/.
MIN_WAYPOINT_SPACING_KM = 50
MAX_WAYPOINT_SPACING_KM = 1000
DEFAULT_WAYPOINT_SPACING_KM = 50


def spacing_or_default(spacing: int | None) -> int:
    return DEFAULT_WAYPOINT_SPACING_KM if spacing is None else spacing


class AdoptionService:
    """Picking a breed and a name creates the strider. Its `adopted_at` is the sign-up date."""

    def __init__(self, session: Session, content: Content):
        self.striders = StriderRepository(session)
        self.content = content

    def adopt(
        self,
        user: User,
        breed: str,
        name: str | None,
        adopted_at: datetime | None = None,
        waypoint_spacing_km: int | None = None,
    ) -> Strider:
        spacing = spacing_or_default(waypoint_spacing_km)
        if breed not in self.content.breeds:
            known = ", ".join(sorted(self.content.breeds)) or "none yet"
            raise AdoptionError(f"Unknown breed {breed!r} (available: {known})")
        if not MIN_WAYPOINT_SPACING_KM <= spacing <= MAX_WAYPOINT_SPACING_KM:
            raise AdoptionError(
                f"Distance between waypoints must be {MIN_WAYPOINT_SPACING_KM} to "
                f"{MAX_WAYPOINT_SPACING_KM} km"
            )
        if self.striders.get_for_user(user.id):
            raise AlreadyAdoptedError("This user already has a strider")
        try:
            name = random_name() if name is None else clean_name(name)
        except ValueError as error:
            raise AdoptionError(str(error)) from error
        return self.striders.create(user.id, breed, name, adopted_at or datetime.now(UTC), spacing)
