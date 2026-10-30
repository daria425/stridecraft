"""Definitions of game content: static things authored in `server/content/`, not player state.
Binary assets they point to live in `assets/` at the repo root.

A file's name is its id (`breeds/cetus.yaml` is the breed "cetus"); the loader fills `id` in, so
files never repeat it. Ids are what the database stores, so never rename or reuse one.
"""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from stridecraft.utils.templates import slots_in

ID_PATTERN = r"^[a-z][a-z0-9_]*$"
# Slots every story text may use; the game fills them in when a scene is shown.
BUILT_IN_SLOTS = frozenset({"strider", "breed"})


class Strict(BaseModel):
    # Strict on purpose: a typo'd field in a YAML file should fail loudly, not be ignored.
    model_config = ConfigDict(frozen=True, extra="forbid")


class ContentModel(Strict):
    id: str = Field(pattern=ID_PATTERN)


class Breed(ContentModel):
    name: str
    description: str
    model: str | None = None  # path to the 3D model under assets/ (repo root), once it exists
    icon: str | None = None  # path to a still image of it under assets/, for cards and profiles


class Landmark(Strict):
    """The authored scene at the end of a leg. Fixed text, no rolling."""

    name: str
    text: str

    @model_validator(mode="after")
    def only_built_in_slots(self) -> "Landmark":
        unknown = slots_in(self.text) - BUILT_IN_SLOTS
        if unknown:
            raise ValueError(f"landmark text uses unknown slots: {sorted(unknown)}")
        return self


class Leg(Strict):
    """A region of the road: `length` waypoints, the last of which is its landmark."""

    id: str = Field(pattern=ID_PATTERN)
    name: str
    tags: list[str] = Field(min_length=1)  # which encounters can happen here
    length: int = Field(gt=0)  # in waypoints, landmark included
    landmark: Landmark


class Journey(ContentModel):
    """The authored road. It starts in the first leg; after each landmark the next leg is rolled
    from the others, so the road never ends and loops once the legs run out."""

    name: str
    intro: str  # shown before the first waypoint
    legs: list[Leg] = Field(min_length=1)

    @model_validator(mode="after")
    def legs_are_unique_and_text_is_fillable(self) -> "Journey":
        ids = [leg.id for leg in self.legs]
        if len(set(ids)) != len(ids):
            raise ValueError("leg ids must be unique")
        unknown = slots_in(self.intro) - BUILT_IN_SLOTS
        if unknown:
            raise ValueError(f"intro uses unknown slots: {sorted(unknown)}")
        return self


class Encounter(ContentModel):
    """A scene template. Each time a waypoint resolves to it, every slot gets one of its values."""

    name: str
    text: str
    tags: list[str] = Field(min_length=1)
    weight: int = Field(default=1, gt=0)  # relative chance among the encounters that fit a leg
    variables: dict[str, list[str]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def slots_and_variables_match(self) -> "Encounter":
        used = slots_in(self.text)
        unknown = used - BUILT_IN_SLOTS - set(self.variables)
        if unknown:
            raise ValueError(f"text uses slots with no variables: {sorted(unknown)}")
        unused = set(self.variables) - used
        if unused:
            raise ValueError(f"variables never used in the text: {sorted(unused)}")
        if set(self.variables) & BUILT_IN_SLOTS:
            raise ValueError(f"variables may not reuse built-in slots {sorted(BUILT_IN_SLOTS)}")
        if any(not values for values in self.variables.values()):
            raise ValueError("every variable needs at least one value")
        return self
