from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from htcondor_dashboard._fastapi import lifespan
from htcondor_dashboard.condor import router as condor_router
from htcondor_dashboard.config import get_template_dir
from htcondor_dashboard.prometheus import router as prometheus_router
from htcondor_dashboard.views import router as view_router

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(condor_router, prefix="/api/v1")
app.include_router(prometheus_router, prefix="/prometheus")
app.include_router(view_router, prefix="/views")

templates = get_template_dir()


@app.get("/", response_class=RedirectResponse)
async def root(request: Request) -> RedirectResponse:
    return RedirectResponse(url=request.url_for("cluster_summary"))


@app.get("/health")
async def health_check() -> JSONResponse:
    """
    Health check endpoint.
    Returns a JSON response with a status indicating the app is up and running.
    """
    return JSONResponse(content={"status": "healthy"}, status_code=200)


@app.get("/debug")
async def debug(request: Request) -> JSONResponse:
    url_list = [
        {"path": route.path, "name": route.name} for route in request.app.routes
    ]
    return JSONResponse(
        content={
            "message": "Hello World",
            "root_path": request.scope.get("root_path"),
            "routes": url_list,
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
