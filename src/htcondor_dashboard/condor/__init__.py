# set of functions that query the HTCondor collector and return the results as pandas dataframes
# from ._pandas import get_jobs_from_submit_node, get_slots_info, get_submit_info, job_info_summary

# __all__ = ["get_jobs_from_submit_node", "get_slots_info", "get_submit_info", "job_info_summary"]

from __future__ import annotations
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import json


from ._pandas import get_submit_info

router = APIRouter(
    tags=["htcondor", "condor"],
    responses={404: {"description": "Not found"}},
)


@router.get("/jobs")
def get_jobs() -> JSONResponse:
    jobs = get_submit_info().to_json(orient="split")
    return JSONResponse(content=json.loads(jobs), status_code=200)
