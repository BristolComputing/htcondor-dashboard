from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from htcondor_dashboard.condor import router as condor_router
from htcondor_dashboard.views import router as view_router
from htcondor_dashboard.config import get_template_dir


import httpx
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.requests_client = httpx.AsyncClient()
    yield
    await app.requests_client.aclose()

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(condor_router, prefix="/api/v1")
app.include_router(view_router, prefix="/views")

templates = get_template_dir()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "message": "Welcome to the HTCondor Dasboard!"},
    )


@app.get("/health")
async def health_check() -> JSONResponse:
    """
    Health check endpoint.
    Returns a JSON response with a status indicating the app is up and running.
    """
    return JSONResponse(content={"status": "healthy"}, status_code=200)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
