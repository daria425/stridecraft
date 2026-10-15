from dataclasses import dataclass

from cryptography.fernet import Fernet

from stridecraft.api.strava_login import StravaLogin
from stridecraft.config import AppConfig
from stridecraft.content.registry import Content
from stridecraft.db.database import Database
from stridecraft.services.importer import Importer
from stridecraft.services.sync_jobs import SyncJobs


@dataclass
class AppState:
    """The long-lived pieces the routes share, built once in `create_app`."""

    config: AppConfig
    database: Database
    content: Content
    cipher: Fernet
    login: StravaLogin
    importer: Importer
    jobs: SyncJobs
