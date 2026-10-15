"""`uv run --env-file .env uvicorn stridecraft.api.main:app --reload`"""

from stridecraft.api.app import create_app

app = create_app()
