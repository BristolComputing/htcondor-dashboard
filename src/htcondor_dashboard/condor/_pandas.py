from __future__ import annotations

from typing import Any

import pandas as pd

from . import _condor as htc


def get_slots_info() -> pd.DataFrame:
    """Converts slot information to a pandas DataFrame"""
    slots_info = htc.get_slots_info()
    slot_info_df = pd.DataFrame.from_records(slots_info).sort_values(by="Machine")
    # remove partitioned slots
    slot_info_df = slot_info_df[slot_info_df["Name"].str.startswith("slot1@")]
    slot_info_df["OS"] = slot_info_df["OpSysAndVer"] + slot_info_df["Microarch"]
    slot_info_df = slot_info_df.drop(columns=["OpSysAndVer", "Microarch", "Disk"])
    to_rename = {
        "Machine": "FQDN",
        "NumDynamicSlots": "Jobs",
        "TotalSlotCpus": "CPUs",
        "TotalSlotGPUs": "GPUs",
        "TotalSlotMemory": "RAM",
        "TotalSlotDisk": "Disk",
        "ChildCpus_summary": "CPUs (Used)",
        "ChildGPUs_summary": "GPUs (Used)",
        "ChildMemory_summary": "RAM (Used)",
        "ChildDisk_summary": "Disk (Used)",
    }
    slot_info_df = slot_info_df.rename(columns=to_rename)

    slot_info_df["node"] = slot_info_df["FQDN"].str.extract(r"^([^\.]+)")
    slot_info_df["RAM [GB]"] = slot_info_df["RAM"] // 1024
    slot_info_df["RAM [GB] (Used)"] = slot_info_df["RAM (Used)"] // 1024
    # slot_info_df["Disk [GB]"] = slot_info_df["Disk"] // 1024 // 1024
    slot_info_df["Disk [MB] (Used)"] = slot_info_df["Disk (Used)"] // 1024
    slot_info_df["Idle Time [h]"] = slot_info_df["TotalTimeUnclaimedIdle"] // 3600
    slot_info_df["Uptime [h]"] = (
        pd.Timestamp.today() - pd.to_datetime(slot_info_df["DaemonStartTime"], unit="s")
    ).dt.days * 24

    return slot_info_df


def job_info_summary(job_info: dict[str, Any]) -> dict[str, Any]:
    job_info_df = pd.DataFrame.from_records(job_info)
    if job_info_df.empty:
        return {
            "Jobs IDLE": 0,
            "Jobs RUNNING": 0,
            "Jobs HELD": 0,
            "Jobs COMPLETED": 0,
        }
    return {
        "Jobs IDLE": len(job_info_df[job_info_df["JobStatus"] == "IDLE"]),
        "Jobs RUNNING": len(job_info_df[job_info_df["JobStatus"] == "RUNNING"]),
        "Jobs HELD": len(job_info_df[job_info_df["JobStatus"] == "HELD"]),
        "Jobs COMPLETED": len(job_info_df[job_info_df["JobStatus"] == "COMPLETED"]),
    }


# def get_job_summary() -> pd.DataFrame:
#     job_info = htc.get_jobs_from_submit_node()
#     job_summary = job_info_summary(job_info)
#     return pd.DataFrame.from_records([job_summary])


# def get_jobs_from_submit_node() -> pd.DataFrame:
#     job_info = htc.get_jobs_from_submit_node()
#     return pd.DataFrame.from_records(job_info)


def get_submit_info(exclude_submit_nodes: tuple[str, ...]) -> pd.DataFrame:
    submit_info = htc.get_submit_info(exclude_submit_nodes)
    result = []
    for schedd_name, job_info in submit_info.items():
        job_summary = job_info_summary(job_info)
        job_summary["Name"] = schedd_name
        result.append(job_summary)
    return pd.DataFrame.from_records(result).sort_values(by="Name")
