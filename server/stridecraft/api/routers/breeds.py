from fastapi import APIRouter

from stridecraft.api.deps import GameContent
from stridecraft.api.schemas import BreedOut, NameOut
from stridecraft.utils.names import random_name

router = APIRouter(tags=["adoption"])


@router.get("/breeds", summary="Breeds that can be adopted")
def list_breeds(content: GameContent) -> list[BreedOut]:
    return [
        BreedOut(id=b.id, name=b.name, description=b.description, model=b.model)
        for b in content.breeds.values()
    ]


@router.get("/names/random", summary="A suggested strider name")
def suggest_name() -> NameOut:
    """A different name on each call; the user may edit it."""
    return NameOut(name=random_name())
