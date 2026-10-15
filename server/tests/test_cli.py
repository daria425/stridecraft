import argparse

import pytest

from stridecraft.cli import Cli
from stridecraft.db.database import Database


@pytest.fixture
def cli(tmp_path):
    return Cli(Database(f"sqlite:///{tmp_path / 'test.db'}"))


@pytest.mark.parametrize("answer, survives", [("y", False), ("Y ", False), ("n", True), ("", True)])
def test_reset_deletes_the_database_only_when_confirmed(cli, monkeypatch, answer, survives):
    monkeypatch.setattr("builtins.input", lambda prompt: answer)

    cli.reset(argparse.Namespace())

    assert cli.database.path.exists() == survives
