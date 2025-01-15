from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

import pandas as pd

from htcondor_dashboard import config

templates = config.get_template_dir()

router = APIRouter(
    tags=["htcondor", "condor"],
    responses={404: {"description": "Not found"}},
)


@router.get("/jobs")
async def get_jobs(request: Request) -> HTMLResponse:
    api_endpoint = "http://localhost:8000/api/v1/jobs"
    settings = config.get_settings()
    requests_client = request.app.requests_client
    r = await requests_client.get(api_endpoint)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.json())

    data = r.json()
    jobs = pd.DataFrame(**data)
    # reorder columns
    jobs = jobs[["Name", "Jobs IDLE", "Jobs RUNNING", "Jobs HELD", "Jobs COMPLETED"]]
    # exclude submit nodes
    jobs = jobs[~jobs["Name"].isin(settings.exclude_submit_nodes)]
    # rename name to submit node
    jobs = jobs.rename(columns={"Name": "Submit Node"})
    # split by LCG nodes and local nodes
    lcg_mask = jobs["Submit Node"].str.contains("lcg")
    lcg_nodes = jobs[lcg_mask]
    local_nodes = jobs[~lcg_mask]

    return templates.TemplateResponse(
        "job_view.html",
        {"request": request, "local_jobs":local_nodes, "remote_jobs": lcg_nodes},
    )
