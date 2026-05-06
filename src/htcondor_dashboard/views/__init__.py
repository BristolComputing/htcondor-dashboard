from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from htcondor_dashboard import config

templates = config.get_template_dir()

router = APIRouter(
    tags=["htcondor", "condor"],
    responses={404: {"description": "Not found"}},
)


@router.get("/jobs/all", name="cluster_summary")
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
        request=request,
        name="index.html",
        context={
            "local_jobs": local_nodes,
            "remote_jobs": lcg_nodes,
            "view_template": "jobs_overview.html",
        },
    )


@router.get("/slots/all", name="node_summary")
async def get_all_slots(request: Request) -> HTMLResponse:
    api_endpoint = "http://localhost:8000/api/v1/slots/all"
    requests_client = request.app.requests_client
    r = await requests_client.get(api_endpoint)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.json())

    data = r.json()
    slots = pd.DataFrame(**data)
    # drop redundant columns
    column_order = [
        "FQDN",
        # "Status",
        "OS",
        "Jobs",
        "TotalLoadAvg",
        "CPUs",
        "CPUs (Used)",
        "GPUs",
        "GPUs (Used)",
        "RAM [GB]",
        "RAM [GB] (Used)",
        # "Disk [GB]",
        "Disk [MB] (Used)",
        "Uptime [h]",
        "Idle Time [h]",
    ]

    slots = slots[column_order]
    # calculate totals for CPUs, GPUs, RAM, Disk and used resources
    totals = slots.sum().drop(["FQDN", "OS", "TotalLoadAvg"])
    totals_df = pd.DataFrame(totals).T

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "slots": slots,
            "totals": totals_df,
            "view_template": "nodes_overview.html",
        },
    )


@router.get("/slots/{node}", name="node_details")
async def get_slots(node: str, request: Request) -> HTMLResponse:
    api_endpoint = f"http://localhost:8000/api/v1/slots/{node}"
    requests_client = request.app.requests_client
    r = await requests_client.get(api_endpoint)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.json())

    data = r.json()
    slots = pd.DataFrame(**data)
    overview_columns = [
        "FQDN",
        "OS",
        "Jobs",
        "TotalLoadAvg",
        "CPUs",
        "CPUs (Used)",
        "GPUs",
        "GPUs (Used)",
        "RAM [GB]",
        "RAM [GB] (Used)",
        "Disk [MB] (Used)",
        "Uptime [h]",
        "Idle Time [h]",
    ]
    overview = slots[overview_columns]
    job_columns = slots.columns[slots.columns.str.contains("Child")]
    job_details = slots[job_columns]
    # all of the rows in job_details are lists, so we need to explode
    job_details = job_details.apply(pd.Series.explode, ignore_index=True)
    # remove the "Child" prefix from the column names
    job_details.columns = job_details.columns.str.replace("Child", "")
    # rename columns and convert units
    # convert disk from KB to MB
    job_details["Disk"] = job_details["Disk"] // 1024
    job_details = job_details.rename(
        columns={
            "Memory": "Memory [MB]",
            "Disk": "Disk [MB]",
            "RemoteUser": "User",
            "RemoteOwner": "Owner",
            "Cpus": "CPUs",
        }
    )

    # reorder columns
    column_order = [
        "User",
        "Owner",
        "AccountingGroup",
        "CPUs",
        "GPUs",
        "Memory [MB]",
        "Disk [MB]",
    ]
    job_details = job_details[column_order]
    # replace NaNs with "---"
    job_details = job_details.fillna("---")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "job_details": job_details,
            "overview": overview,
            "view_template": "node_details.html",
        },
    )


@router.get("/submit/all", name="submit_summary")
async def get_all_submit_nodes(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"view_template": "submit_overview.html"},
    )
