import json
import random
from pathlib import Path

from stridecraft.config import NAMES_PATH

MAX_NAME_LENGTH = 30


def random_name(path: Path = NAMES_PATH) -> str:
    """A default strider name for the user to accept or edit."""
    return random.choice(json.loads(path.read_text(encoding="utf-8"))["names"])


def clean_name(name: str) -> str:
    """The name as it will be stored: trimmed, and never empty or absurdly long."""
    name = name.strip()
    if not name:
        raise ValueError("A strider needs a name")
    if len(name) > MAX_NAME_LENGTH:
        raise ValueError(f"Name is too long ({len(name)} characters, max {MAX_NAME_LENGTH})")
    return name
