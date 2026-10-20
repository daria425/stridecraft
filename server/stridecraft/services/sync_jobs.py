"""Runs imports in the background and remembers how each user's last one went.

Status lives in memory: fine for one server process, and an import is idempotent, so after a
restart the state is just "idle" and the next sync catches up. Imports run one at a time across
all users because Strava's rate limit belongs to the app, not to a user.
"""

import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from stridecraft.errors import StridecraftError, SyncInProgressError
from stridecraft.services.sync import SyncResult

logger = logging.getLogger(__name__)


class SyncState(StrEnum):
    IDLE = "idle"
    RUNNING = "running"
    FAILED = "failed"


@dataclass(frozen=True)
class SyncStatus:
    state: SyncState = SyncState.IDLE
    result: SyncResult | None = None  # the last import that finished
    error: str | None = None  # why the last import failed


class SyncJobs:
    def __init__(self):
        self.statuses: dict[int, SyncStatus] = {}
        self.status_lock = threading.Lock()
        self.strava_lock = threading.Lock()  # one import at a time, app-wide

    def status(self, user_id: int) -> SyncStatus:
        with self.status_lock:
            return self.statuses.get(user_id, SyncStatus())

    def start(self, user_id: int) -> None:
        """Mark the import as running, or refuse if this user already has one going."""
        with self.status_lock:
            previous = self.statuses.get(user_id, SyncStatus())
            if previous.state is SyncState.RUNNING:
                raise SyncInProgressError("An import is already running")
            self.statuses[user_id] = SyncStatus(SyncState.RUNNING, previous.result)

    def forget(self, user_id: int) -> None:
        """Drop the remembered outcome (the user started over), unless an import is running."""
        with self.status_lock:
            if self.statuses.get(user_id, SyncStatus()).state is SyncState.RUNNING:
                raise SyncInProgressError("An import is running; wait for it to finish")
            self.statuses.pop(user_id, None)

    def run(self, user_id: int, import_runs: Callable[[], SyncResult]) -> None:
        """Do the import (in a background task) and record the outcome. Never raises; a failure is
        logged with its traceback."""
        try:
            with self.strava_lock:
                result = import_runs()
        except Exception as error:
            logger.exception("Import failed for user %s", user_id)
            message = str(error) if isinstance(error, StridecraftError) else "The import failed"
            self.finish(user_id, SyncStatus(SyncState.FAILED, self.status(user_id).result, message))
        else:
            self.finish(user_id, SyncStatus(SyncState.IDLE, result))

    def finish(self, user_id: int, status: SyncStatus) -> None:
        with self.status_lock:
            self.statuses[user_id] = status
