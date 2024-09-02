# https://github.com/niclabs/htcondor-monitor/blob/master/CondorExporter/exporter/CondorExporter.py

import htcondor
import pandas as pd


def job_status_to_str(status):
    return {
        htcondor.JobStatus.IDLE: "IDLE",
        htcondor.JobStatus.RUNNING: "RUNNING",
        htcondor.JobStatus.REMOVED: "REMOVED",
        htcondor.JobStatus.COMPLETED: "COMPLETED",
        htcondor.JobStatus.HELD: "HELD",
        htcondor.JobStatus.SUSPENDED: "SUSPENDED",
    }.get(status, "UNKNOWN")


def get_all_submitters():
    collector = htcondor.Collector()
    projection = ["Name", "MyAddress"]
    all_submitters_query = collector.query(
        htcondor.AdTypes.Submitter, projection=projection
    )
    return [htcondor.Schedd(submitter) for submitter in all_submitters_query]


def get_submit_names():
    collector = htcondor.Collector()
    ads = collector.locateAll(htcondor.DaemonTypes.Schedd)

    return [node["Name"] for node in ads]


def _process_job_ad(job, ad):
    return job.get(ad, "")


def _jobs_info_to_df(jobs_info):
    return pd.DataFrame.from_records(jobs_info)


def _produce_job_info_summary(job_info):
    if job_info.empty:
        return {
            "Jobs IDLE": 0,
            "Jobs RUNNING": 0,
            "Jobs HELD": 0,
            "Jobs COMPLETED": 0,
        }
    return {
        "Jobs IDLE": len(job_info[job_info["JobStatus"] == "IDLE"]),
        "Jobs RUNNING": len(job_info[job_info["JobStatus"] == "RUNNING"]),
        "Jobs HELD": len(job_info[job_info["JobStatus"] == "HELD"]),
        "Jobs COMPLETED": len(job_info[job_info["JobStatus"] == "COMPLETED"]),
    }


def get_jobs_from_submit_node(schedd):
    projection = [
        "Owner",
        "User",
        "ExitStatus",
        "Cmd",
        "ClusterId",
        "ProcId",
        "GlobalJobId",
        "JobStatus",
        "RemoteSlotID",
        "RemoteHost",
    ]
    job_ads = schedd.xquery(projection=projection)
    result = []
    for job in job_ads:
        info = {name: _process_job_ad(job, name) for name in projection}
        info["JobStatus"] = job_status_to_str(info["JobStatus"])
        result.append(info)
    job_info = _jobs_info_to_df(result)
    return job_info, _produce_job_info_summary(job_info)


def get_submit_info():
    collector = htcondor.Collector()
    ads = collector.locateAll(htcondor.DaemonTypes.Schedd)
    names = [node["Name"] for node in ads]
    schedds = [htcondor.Schedd(node) for node in ads]
    return {
        name: get_jobs_from_submit_node(schedd) for name, schedd in zip(names, schedds)
    }


def _process_slot_ad(slot, ad):
    if ad == "Start":
        value = slot.get(ad, False)
        if value:
            return "ON"
        return "DRAINING"
    return slot.get(ad, "")


def _produce_slot_info_summary(slot):
    summary = {}
    for key, value in slot.items():
        if key.startswith("Child") and type(value) is list:
            # if "User" in key or "Group" in key:
            if any(x in key for x in ["User", "Group", "Owner"]):
                summary[key] = value
                continue
            summary[key + "_summary"] = sum(value)
        summary[key] = value
    return summary


def _slots_info_to_df(slots_info):
    slot_info = pd.DataFrame.from_records(slots_info).sort_values(by="Machine")
    # remove partitioned slots
    slot_info = slot_info[slot_info["Name"].str.startswith("slot1@")]
    slot_info["OS"] = slot_info["OpSysAndVer"] + "/" + slot_info["Microarch"]
    slot_info = slot_info.drop(columns=["OpSysAndVer", "Microarch", "Disk"])
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
    slot_info = slot_info.rename(columns=to_rename)

    slot_info["node"] = slot_info["FQDN"].str.extract(r"^([^\.]+)")
    slot_info["RAM [GB]"] = slot_info["RAM"] // 1024
    slot_info["RAM [GB] (Used)"] = slot_info["RAM (Used)"] // 1024
    # slot_info["Disk [GB]"] = slot_info["Disk"] // 1024 // 1024
    slot_info["Disk [MB] (Used)"] = slot_info["Disk (Used)"] // 1024
    slot_info["Idle Time [h]"] = slot_info["TotalTimeUnclaimedIdle"] // 3600
    slot_info["Uptime [h]"] = (pd.Timestamp.today() - pd.to_datetime(slot_info["DaemonStartTime"], unit="s")).dt.days * 24

    return slot_info


def get_slots_info():
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

    return _slots_info_to_df(result)
