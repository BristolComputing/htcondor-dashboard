# set of functions that query the HTCondor collector and return the results as pandas dataframes
# from ._pandas import get_jobs_from_submit_node, get_slots_info, get_submit_info, job_info_summary

# __all__ = ["get_jobs_from_submit_node", "get_slots_info", "get_submit_info", "job_info_summary"]

from __future__ import annotations

import json

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..config import get_settings
from ._pandas import get_slots_info, get_submit_info

__all__ = ["get_slots_info", "get_submit_info"]

router = APIRouter(
    tags=["htcondor", "condor"],
    responses={404: {"description": "Not found"}},
)


@router.get("/jobs", name="api_v1_get_jobs")
def get_jobs() -> JSONResponse:
    jobs = get_submit_info(get_settings().exclude_submit_nodes).to_json(orient="split")
    return JSONResponse(content=json.loads(jobs), status_code=200)


@router.get("/slots/all")
def get_all_slots() -> JSONResponse:
    slots = get_slots_info().to_json(orient="split")
    return JSONResponse(content=json.loads(slots), status_code=200)


@router.get("/slots/{hostname}")
def get_slots(hostname: str) -> JSONResponse:
    slots = get_slots_info()
    slots_json = slots[slots["FQDN"].str.contains(hostname)].to_json(orient="split")

    return JSONResponse(content=json.loads(slots_json), status_code=200)


@router.get("/config")
async def config() -> JSONResponse:
    config = get_settings()
    json_content = config.model_dump(mode="json")
    return JSONResponse(content=json_content, status_code=200)
