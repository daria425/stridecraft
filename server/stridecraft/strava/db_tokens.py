from cryptography.fernet import Fernet

from stridecraft.db.database import Database
from stridecraft.db.repositories import TokenRepository
from stridecraft.strava.auth import Tokens


class DbTokenStore:
    """One user's Strava tokens in the database. Same load/save as the file `TokenStore`, so
    `StravaAuth` works with either. Each call uses its own session: a token refresh can happen
    in the middle of a background import."""

    def __init__(self, database: Database, cipher: Fernet, user_id: int):
        self.database = database
        self.cipher = cipher
        self.user_id = user_id

    def load(self) -> Tokens | None:
        with self.database.session() as session:
            return TokenRepository(session, self.cipher).get(self.user_id)

    def save(self, tokens: Tokens) -> None:
        with self.database.session() as session:
            TokenRepository(session, self.cipher).save(self.user_id, tokens)
            session.commit()
