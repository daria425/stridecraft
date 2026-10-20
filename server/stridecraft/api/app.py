from cryptography.fernet import Fernet
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from stridecraft.api.errors import handle_stridecraft_error
from stridecraft.api.routers import auth, breeds, dev, me
from stridecraft.api.state import AppState
from stridecraft.api.strava_login import StravaLogin
from stridecraft.config import ASSETS_DIR, AppConfig, StravaConfig
from stridecraft.content.registry import Content
from stridecraft.db.database import Database
from stridecraft.errors import StridecraftError
from stridecraft.services.importer import Importer
from stridecraft.services.sync_jobs import SyncJobs

SESSION_MAX_AGE_S = 30 * 86400

DESCRIPTION = """
Stridecraft turns real Strava runs into a creature-collecting RPG.

**Onboarding:** send the browser to `GET /auth/strava/login`. When it comes back to the frontend
logged in, call `GET /me`; if `strider` is `null`, show the adoption page (`GET /breeds`,
`GET /names/random`, then `POST /me/strider`) and follow the import with `GET /me/sync`.

Login is a signed cookie, so `fetch` calls need `credentials: "include"`.
"""


def route_name_as_id(route: APIRoute) -> str:
    """Clean operation ids (`get_me`, not `get_me_me_get`) for the frontend's generated client."""
    return route.name


def create_app(
    config: AppConfig | None = None,
    strava: StravaConfig | None = None,
    database: Database | None = None,
    login: StravaLogin | None = None,
) -> FastAPI:
    """Everything is injectable so tests can use an in-memory database and a fake Strava login."""
    config = config or AppConfig.from_env()
    strava = strava or StravaConfig.from_env()
    database = database or Database()
    cipher = Fernet(config.token_encryption_key.encode())

    app = FastAPI(
        title="Stridecraft API",
        version="0.1.0",
        description=DESCRIPTION,
        generate_unique_id_function=route_name_as_id,
    )
    app.state.stridecraft = AppState(
        config=config,
        database=database,
        content=Content.load(),
        cipher=cipher,
        login=login or StravaLogin(strava),
        importer=Importer(database, strava, cipher),
        jobs=SyncJobs(),
    )
    app.add_middleware(
        SessionMiddleware,
        secret_key=config.session_secret,
        same_site="lax",
        https_only=config.public_url.startswith("https"),
        max_age=SESSION_MAX_AGE_S,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[config.frontend_url],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_exception_handler(StridecraftError, handle_stridecraft_error)
    # Dev convenience; in production ASSET_BASE_URL points at a CDN or static host (journal/0013).
    if ASSETS_DIR.is_dir():
        app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")
    for router in (auth.router, me.router, breeds.router):
        app.include_router(router)
    if config.dev_tools:
        app.include_router(dev.router)
    return app
