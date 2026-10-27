"""Story text with `{slots}`: the slots a text uses, and filling them in."""

from string import Formatter


def slots_in(text: str) -> set[str]:
    """Every `{slot}` in the text. Anything fancier than a plain name (`{a.b}`, `{}`) is returned
    as written, so the caller's "is this slot known" check rejects it."""
    return {field for _, field, _, _ in Formatter().parse(text) if field is not None}


def fill(text: str, values: dict[str, str]) -> str:
    return text.format_map(values)
