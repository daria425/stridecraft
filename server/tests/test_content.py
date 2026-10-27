import pytest

from stridecraft.content.registry import Content, ContentError


def write_breed(folder, filename, body):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / filename).write_text(body)


def test_shipped_content_is_valid():
    """Every real file in server/content/ loads, so a bad edit fails here, not at runtime."""
    assert "cetus" in Content.load().breeds


def test_filename_becomes_the_id(tmp_path):
    write_breed(tmp_path / "breeds", "hydra.yaml", "name: Hydra\ndescription: Many heads.\n")
    breed = Content.load(tmp_path).breeds["hydra"]
    assert breed.id == "hydra"
    assert breed.model is None


@pytest.mark.parametrize(
    "filename, body",
    [
        ("typo.yaml", "name: X\ndescription: Y\nmodle: a.glb\n"),  # unknown field
        ("missing.yaml", "name: X\n"),  # description required
        ("Bad-Id.yaml", "name: X\ndescription: Y\n"),  # id must be lower_snake
        ("norway.yaml", "name: no\ndescription: Y\n"),  # YAML reads bare `no` as False
        ("explicit.yaml", "id: other\nname: X\ndescription: Y\n"),  # id comes from filename
        ("empty.yaml", ""),
        ("list.yaml", "- a\n- b\n"),
        ("broken.yaml", "name: [unclosed\n"),
    ],
)
def test_bad_files_fail_naming_the_file(tmp_path, filename, body):
    write_breed(tmp_path / "breeds", filename, body)
    with pytest.raises(ContentError, match=filename):
        Content.load(tmp_path)


def test_missing_folder_means_no_content(tmp_path):
    assert Content.load(tmp_path).breeds == {}


ENCOUNTER = "name: E\ntags: [sea]\ntext: Hello {strider}.\n"
JOURNEY = """name: J
intro: Hi {strider}.
legs:
  - id: a
    name: A
    tags: [sea]
    length: 3
    landmark: {name: L, text: Done}
  - id: b
    name: B
    tags: [sea]
    length: 2
    landmark: {name: M, text: Done}
"""


def write_road(tmp_path, journey=JOURNEY, encounter=ENCOUNTER):
    write_breed(tmp_path / "journeys", "voyage.yaml", journey)
    write_breed(tmp_path / "encounters", "e.yaml", encounter)
    return Content.load(tmp_path)


def test_a_well_formed_road_loads(tmp_path):
    assert [leg.id for leg in write_road(tmp_path).journey.legs] == ["a", "b"]


@pytest.mark.parametrize(
    "encounter",
    [
        "name: E\ntags: [sea]\ntext: A {nope}.\n",  # slot with no variable
        "name: E\ntags: [sea]\ntext: A.\nvariables: {x: [1]}\n",  # variable never used
        "name: E\ntags: [sea]\ntext: A {strider}.\nvariables: {strider: [x]}\n",  # shadows built-in
        "name: E\ntags: [sea]\ntext: A {x}.\nvariables: {x: []}\n",  # nothing to choose from
        "name: E\ntags: [sea]\ntext: A {x.y}.\nvariables: {x: [a]}\n",  # attribute access
        "name: E\ntags: []\ntext: A.\n",  # fits nowhere
        "name: E\ntags: [sea]\ntext: A.\nweight: 0\n",
    ],
)
def test_bad_encounters_are_rejected(tmp_path, encounter):
    with pytest.raises(ContentError, match="e.yaml"):
        write_road(tmp_path, encounter=encounter)


@pytest.mark.parametrize(
    "journey",
    [
        JOURNEY.replace("    length: 3\n", ""),  # every leg needs a length
        JOURNEY.replace("    length: 2\n", ""),  # including the last: none is open-ended
        JOURNEY.replace("    landmark: {name: M, text: Done}\n", ""),  # and a landmark
        JOURNEY.replace("id: b", "id: a"),  # duplicate leg ids
        JOURNEY.replace("Done", "Done {nobody}"),  # unknown slot in a landmark
        JOURNEY.replace("Hi {strider}", "Hi {nobody}"),  # unknown slot in the intro
    ],
)
def test_bad_roads_are_rejected(tmp_path, journey):
    with pytest.raises(ContentError, match="voyage.yaml"):
        write_road(tmp_path, journey=journey)


def test_a_leg_nothing_can_happen_in_is_rejected(tmp_path):
    with pytest.raises(ContentError, match="no encounter has a tag"):
        write_road(tmp_path, encounter=ENCOUNTER.replace("sea", "desert"))
