from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import ValidationError

from stridecraft.config import CONTENT_DIR
from stridecraft.content.models import Breed, ContentModel, Encounter, Journey

T = TypeVar("T", bound=ContentModel)

# The one road every strider walks. More journeys may come; this is the one in use.
JOURNEY_ID = "voyage"


class ContentError(ValueError):
    """A content file is malformed; the message names the file."""


class Content:
    """Every piece of game content, loaded once and validated. Look things up by id."""

    def __init__(
        self,
        breeds: dict[str, Breed],
        journeys: dict[str, Journey] | None = None,
        encounters: dict[str, Encounter] | None = None,
    ):
        self.breeds = breeds
        self.journeys = journeys or {}
        self.encounters = encounters or {}

    @property
    def journey(self) -> Journey:
        if JOURNEY_ID not in self.journeys:
            raise ContentError(f"journeys/{JOURNEY_ID}.yaml is missing")
        return self.journeys[JOURNEY_ID]

    @classmethod
    def load(cls, directory: Path = CONTENT_DIR) -> "Content":
        content = cls(
            breeds=cls.load_kind(directory / "breeds", Breed),
            journeys=cls.load_kind(directory / "journeys", Journey),
            encounters=cls.load_kind(directory / "encounters", Encounter),
        )
        content.check_references()
        return content

    def check_references(self) -> None:
        """Content kinds point at each other by tag; a leg nothing can happen in is a mistake."""
        for journey in self.journeys.values():
            for leg in journey.legs:
                if not any(set(leg.tags) & set(e.tags) for e in self.encounters.values()):
                    raise ContentError(
                        f"journeys/{journey.id}.yaml: no encounter has a tag of leg {leg.id!r} "
                        f"({', '.join(leg.tags)})"
                    )

    @classmethod
    def load_kind(cls, folder: Path, model: type[T]) -> dict[str, T]:
        """One `<id>.yaml` per entity in `folder`; the filename becomes the entity's id."""
        entries: dict[str, T] = {}
        for path in sorted(folder.glob("*.yaml")):
            entries[path.stem] = cls.load_file(path, model)
        return entries

    @classmethod
    def load_file(cls, path: Path, model: type[T]) -> T:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as error:
            raise ContentError(f"{path}: not valid YAML ({error})") from error
        if not isinstance(data, dict):
            raise ContentError(f"{path}: expected key: value pairs at the top level")
        if "id" in data:
            raise ContentError(f"{path}: remove `id`, the filename is the id")
        try:
            return model.model_validate({**data, "id": path.stem})
        except ValidationError as error:
            raise ContentError(f"{path}: {error}") from error
