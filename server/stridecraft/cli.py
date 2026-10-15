"""Command line for the single-user phase (no web login yet):

uv run --env-file .env python -m stridecraft.cli adopt --breed cetus
uv run --env-file .env python -m stridecraft.cli sync
uv run --env-file .env python -m stridecraft.cli status
uv run --env-file .env python -m stridecraft.cli rebuild --breed cetus --name X --adopted-at D
"""

import argparse
from datetime import UTC, datetime
from functools import cached_property

from sqlalchemy.orm import Session

from stridecraft.config import TOKENS_PATH, StravaConfig
from stridecraft.content.registry import Content
from stridecraft.db.database import Database
from stridecraft.db.repositories import RunRepository, StriderRepository, UserRepository
from stridecraft.models import User
from stridecraft.services.adoption import AdoptionError, AdoptionService
from stridecraft.services.sync import NoStriderError, SyncResult, SyncService
from stridecraft.stats.stats_calculator import Stats
from stridecraft.strava.auth import StravaAuth, TokenStore
from stridecraft.strava.client import StravaClient
from stridecraft.utils.names import random_name


def parse_moment(text: str) -> datetime:
    """ISO date or datetime; without a time zone it is read as UTC."""
    moment = datetime.fromisoformat(text)
    return moment if moment.tzinfo else moment.replace(tzinfo=UTC)


class Cli:
    def __init__(self, database: Database | None = None):
        self.database = database or Database()
        self.content = Content.load()

    @cached_property
    def client(self) -> StravaClient:
        auth = StravaAuth(StravaConfig.from_env(), TokenStore(TOKENS_PATH))
        auth.ensure_authorized()
        return StravaClient(auth)

    def ensure_user(self, session: Session) -> User:
        """The Strava account we're logged into, stored on first use."""
        athlete = self.client.athlete()
        users = UserRepository(session)
        user = users.get_by_strava_id(athlete["id"])
        if user is None:
            user = users.create(
                athlete["id"],
                athlete.get("username"),
                athlete.get("firstname"),
                athlete.get("profile"),
            )
            session.commit()
        return user

    def adopt(self, args: argparse.Namespace) -> None:
        name = args.name or random_name()
        with self.database.session() as session:
            user = self.ensure_user(session)
            adopted_at = parse_moment(args.adopted_at) if args.adopted_at else None
            strider = AdoptionService(session, self.content).adopt(
                user, args.breed, name, adopted_at
            )
            session.commit()
            print(f"Adopted {strider.name} the {strider.breed}.")
            self.run_sync(session, user)

    def sync(self, args: argparse.Namespace) -> None:
        with self.database.session() as session:
            self.run_sync(session, self.ensure_user(session))

    def run_sync(self, session: Session, user: User) -> None:
        result = SyncService(self.client, session).sync(user)
        self.print_sync(result)
        self.print_stats(session, user)

    def status(self, args: argparse.Namespace) -> None:
        with self.database.session() as session:
            user = UserRepository(session).first()
            strider = user and StriderRepository(session).get_for_user(user.id)
            if strider is None:
                print("No strider yet: run `adopt`.")
                return
            print(f"{strider.name} the {strider.breed}, adopted {strider.adopted_at:%Y-%m-%d}")
            print(f"Last synced: {user.last_synced_at or 'never'}")
            self.print_stats(session, user)

    def rebuild(self, args: argparse.Namespace) -> None:
        """Schema changed? Wipe the database and rebuild it from Strava (journal/0006)."""
        if self.wipe_after_confirming("rebuild from Strava"):
            self.database = Database(self.database.url)
            self.adopt(args)

    def reset(self, args: argparse.Namespace) -> None:
        """Remove the strider and everything stored. Strava tokens are kept."""
        if self.wipe_after_confirming("start over"):
            print("Database deleted. Run `adopt` for a new strider.")

    def wipe_after_confirming(self, purpose: str) -> bool:
        answer = input(f"Delete {self.database.path} and {purpose}? [y/N] ")
        if answer.strip().lower() != "y":
            print("Nothing deleted.")
            return False
        self.database.wipe()
        return True

    @staticmethod
    def print_sync(result: SyncResult) -> None:
        print(f"{result.new_runs} new runs ({result.baseline_runs} before adoption: baseline only)")

    @staticmethod
    def print_stats(session: Session, user: User) -> None:
        stats = Stats.total(RunRepository(session).gains(user.id))
        print(f"  Speed {stats.speed:.3f}  Endurance {stats.endurance:.3f}")
        print(f"  Hills {stats.hills:.3f}  Consistency {stats.consistency:.3f}")


def build_parser(breeds: list[str]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="stridecraft")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("sync", help="fetch new runs from Strava and store their gains")
    commands.add_parser("status", help="show the strider and its stats (no Strava call)")
    commands.add_parser("reset", help="delete the strider and all stored runs (keeps Strava login)")
    for name, helptext, required in [
        ("adopt", "create your strider, then sync", False),
        ("rebuild", "wipe the database, re-adopt and re-sync", True),
    ]:
        command = commands.add_parser(name, help=helptext)
        command.add_argument("--breed", required=True, choices=breeds)
        command.add_argument("--name", help="default: a random name from names_src.json")
        command.add_argument("--adopted-at", required=required, help="ISO date, default: now")
    return parser


def main() -> None:
    cli = Cli()
    args = build_parser(sorted(cli.content.breeds)).parse_args()
    try:
        getattr(cli, args.command)(args)
    except (AdoptionError, NoStriderError) as error:
        raise SystemExit(str(error)) from error


if __name__ == "__main__":
    main()
