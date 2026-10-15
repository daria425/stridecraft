"""Definitions of game content: static things authored in `server/content/`, not player state.

A file's name is its id (`breeds/cetus.yaml` is the breed "cetus"); the loader fills `id` in, so
files never repeat it. Ids are what the database stores, so never rename or reuse one.
"""

from pydantic import BaseModel, ConfigDict, Field

ID_PATTERN = r"^[a-z][a-z0-9_]*$"


class ContentModel(BaseModel):
    # Strict on purpose: a typo'd field in a YAML file should fail loudly, not be ignored.
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(pattern=ID_PATTERN)


class Breed(ContentModel):
    name: str
    description: str
    model: str | None = None  # path to the 3D model under server/static/, once it exists
