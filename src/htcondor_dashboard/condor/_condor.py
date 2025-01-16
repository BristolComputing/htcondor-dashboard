from __future__ import annotations

from typing import Any

# inspired by https://github.com/niclabs/htcondor-monitor/blob/master/CondorExporter/exporter/CondorExporter.py
import htcondor2 as htcondor
from cachetools import TTLCache, cached


def job_status_to_str(status: int) -> str:
    return {
        htcondor.JobStatus.IDLE: "IDLE",
        htcondor.JobStatus.RUNNING: "RUNNING",
        htcondor.JobStatus.REMOVED: "REMOVED",
        htcondor.JobStatus.COMPLETED: "COMPLETED",
        htcondor.JobStatus.HELD: "HELD",
        htcondor.JobStatus.SUSPENDED: "SUSPENDED",
    }.get(status, "UNKNOWN")


def get_all_submitters(
    exclude_submit_nodes: list[str] | None = None,
) -> list[htcondor.Schedd]:
    if exclude_submit_nodes is None:
        exclude_submit_nodes = []
    collector = htcondor.Collector()
    projection = ["Name", "MyAddress"]
    all_submitters_query = collector.query(
        htcondor.AdTypes.Submitter, projection=projection
    )
    return [
        htcondor.Schedd(submitter)
        for submitter in all_submitters_query
        if submitter["Name"] not in exclude_submit_nodes
    ]


def get_submit_names(exclude_submit_nodes: list[str] | None = None) -> list[str]:
    if exclude_submit_nodes is None:
        exclude_submit_nodes = []
    collector = htcondor.Collector()
    ads = collector.locateAll(htcondor.DaemonTypes.Schedd)

    return [node["Name"] for node in ads if node["Name"] not in exclude_submit_nodes]


def _process_job_ad(job: Any, ad: str) -> Any:
    return job.get(ad, "")


def get_jobs_from_submit_node(schedd: htcondor.Schedd) -> list[dict[str, Any]]:
    projection = [
        "Owner",
        "User",
        "ExitStatus",
        "Cmd",
        "ClusterId",
        "ProcId",
        "GlobalJobId",
        "JobStatus",
        "RemoteHost",
    ]
    job_ads = schedd.query(projection=projection)
    result = []
    for job in job_ads:
        info = {name: _process_job_ad(job, name) for name in projection}
        info["JobStatus"] = job_status_to_str(info["JobStatus"])
        result.append(info)

    return result


@cached(cache=TTLCache(maxsize=1024, ttl=60))
def get_submit_info(exclude_submit_nodes: list[str] | None = None) -> dict[str, Any]:
    collector = htcondor.Collector()
    ads = collector.locateAll(htcondor.DaemonTypes.Schedd)
    names = [node["Name"] for node in ads]
    schedds = [htcondor.Schedd(node) for node in ads]
    if exclude_submit_nodes is None:
        exclude_submit_nodes = []
    return {
        name: get_jobs_from_submit_node(schedd)
        for name, schedd in zip(names, schedds)
        if name not in exclude_submit_nodes
    }


def _process_slot_ad(slot: Any, ad: str) -> Any:
    if ad == "Start":
        value = slot.get(ad, False)
        if value:
            return "ON"
        return "DRAINING"
    return slot.get(ad, "")


def _produce_slot_info_summary(slot: dict[str, Any]) -> dict[str, Any]:
    summary = {}
    for key, value in slot.items():
        if key.startswith("Child") and type(value) is list:
            # if "User" in key or "Group" in key:
            if any(x in key for x in ["User", "Group", "Owner"]):
                summary[key] = value
                continue
            summary[key + "_summary"] = sum(value)  # type:ignore[assignment]
        summary[key] = value
    return summary


@cached(cache=TTLCache(maxsize=1024, ttl=60))
def get_slots_info() -> list[dict[str, Any]]:
    """Queries the collector for all available slots (startds for each worker node)"""
    collector = htcondor.Collector()
    projection = [
        "Machine",
        "Start",
        "OpSysAndVer",
        "Microarch",
        "DetectedCpus",
        "TotalSlotCpus",
        "DetectedGPUs",
        "TotalSlotGPUs",
        "Name",
        # "SlotID", #useless, always 1
        "Activity",
        # "MyAddress",
        "Disk",
        "TotalDisk",
        "TotalSlotDisk",
        "Memory",
        "DetectedMemory",
        "TotalMemory",
        "TotalSlotMemory",
        "JobStarts",
        "LastUpdate",
        "TotalLoadAvg",
        "NumDynamicSlots",
        "ChildCpus",
        "ChildGPUs",
        "ChildMemory",
        "ChildDisk",
        "ChildRemoteUser",
        "ChildAccountingGroup",
        "ChildRemoteOwner",
        "TotalTimeUnclaimedIdle",
        "DaemonStartTime",
    ]
    slots_info = collector.query(htcondor.AdTypes.Startd)
    result = []
    for slot in slots_info:
        info = {name: _process_slot_ad(slot, name) for name in projection}
        info = _produce_slot_info_summary(info)
        result.append(info)

    return result
