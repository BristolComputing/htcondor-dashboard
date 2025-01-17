from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

import httpx
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    app.requests_client = httpx.AsyncClient()  # type: ignore[attr-defined]
    yield
    await app.requests_client.aclose()  # type: ignore[attr-defined]
