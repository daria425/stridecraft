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
