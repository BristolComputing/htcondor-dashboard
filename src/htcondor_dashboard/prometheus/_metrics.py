from __future__ import annotations

from typing import Any

from cachetools import TTLCache, cached
from prometheus_client import Gauge

from ..condor import get_submit_info
from ..config import get_settings

METRICS: dict[str, Any] = {}


def summary_metrics() -> dict[str, Any]:
    metrics = {}
    metrics["htcondor_jobs_total"] = Gauge(
        "htcondor_jobs_total", "Total number of jobs", ["submit_node", "status"]
    )
    return metrics


def create_metrics() -> None:
    if METRICS:
        return
    METRICS.update(summary_metrics())
    METRICS["htcondor_jobs_held_total"] = Gauge(
        "htcondor_jobs_held_total", "Number of jobs held", ["hold_reason"]
    )


def fill_submit_info() -> None:
    submit_info = get_submit_info(get_settings().exclude_submit_nodes)
    columns = submit_info.columns
    for _, row in submit_info.iterrows():
        submit_node = row["Name"]
        # job status columns include "Jobs " prefix
        for column in columns:
            if column.startswith("Jobs "):
                status = column.replace("Jobs ", "")
                count = row[column]
                METRICS["htcondor_jobs_total"].labels(submit_node, status).set(count)


def fill_metrics() -> None:
    fill_submit_info()


@cached(cache=TTLCache(maxsize=1024, ttl=60))
def load() -> dict[str, Any]:
    create_metrics()
    fill_metrics()
    return METRICS
