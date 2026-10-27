from cryptography.fernet import Fernet

from stridecraft.config import StravaConfig
from stridecraft.content.registry import Content
from stridecraft.db.database import Database
from stridecraft.db.repositories import UserRepository
from stridecraft.errors import NotAuthorizedError
from stridecraft.services.sync import SyncResult, SyncService
from stridecraft.strava.auth import StravaAuth
from stridecraft.strava.client import StravaClient
from stridecraft.strava.db_tokens import DbTokenStore


class Importer:
    """Imports one user's runs from Strava using that user's own stored login.

    Opens its own session and Strava client each time: it runs in a background task, long after
    the request that started it (and its session) is gone, and users must never share a client.
    """

    def __init__(self, database: Database, strava: StravaConfig, cipher: Fernet, content: Content):
        self.database = database
        self.content = content
        self.strava = strava
        self.cipher = cipher

    def import_for(self, user_id: int) -> SyncResult:
        with self.database.session() as session:
            user = UserRepository(session).get(user_id)
            if user is None:
                raise NotAuthorizedError("This user no longer exists")
            return SyncService(self.client_for(user_id), session, self.content).sync(user)

    def client_for(self, user_id: int) -> StravaClient:
        store = DbTokenStore(self.database, self.cipher, user_id)
        return StravaClient(StravaAuth(self.strava, store))
