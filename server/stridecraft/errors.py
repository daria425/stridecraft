"""Errors a caller can catch and show. One module so the API layer can map them all in one place.

Messages are plain English for a person and never mention commands or flags: each caller (CLI
today, API route later) decides what to do about them.
"""


class StridecraftError(Exception):
    """Base class: catch this at the top level (CLI, API route) to handle anything expected."""


class StravaError(StridecraftError):
    """Strava failed or could not be reached; trying again later may work."""


class RateLimitError(StravaError):
    """Strava is limiting our requests; wait a few minutes."""


class NotAuthorizedError(StridecraftError):
    """Strava access is missing, expired or revoked; the user must connect Strava again."""


class NoStriderError(StridecraftError):
    """The user has no strider yet, so there is nothing to sync."""


class AdoptionError(StridecraftError):
    """The breed, name or user is not valid for adopting a strider."""
