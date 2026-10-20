"""`uv run --env-file .env uvicorn stridecraft.api.main:app --reload`"""

import logging

from stridecraft.api.app import create_app

# Our own messages at INFO; everything else (httpx, authlib...) stays at warnings.
logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logging.getLogger("stridecraft").setLevel(logging.INFO)

app = create_app()
