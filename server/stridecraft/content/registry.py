from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import ValidationError

from stridecraft.config import CONTENT_DIR
from stridecraft.content.models import Breed, ContentModel

T = TypeVar("T", bound=ContentModel)


class ContentError(ValueError):
    """A content file is malformed; the message names the file."""


class Content:
    """Every piece of game content, loaded once and validated. Look things up by id."""

    def __init__(self, breeds: dict[str, Breed]):
        self.breeds = breeds

    @classmethod
    def load(cls, directory: Path = CONTENT_DIR) -> "Content":
        return cls(breeds=cls.load_kind(directory / "breeds", Breed))

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
