# https://github.com/niclabs/htcondor-monitor/blob/master/CondorExporter/exporter/CondorExporter.py

import htcondor
import pandas as pd

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

def _process_slot_ad(slot, ad):
    if ad == "Start":
        value = slot.get(ad, False)
        if value:
            return "ON"
        return "DRAINING"
    return slot.get(ad, "")

def _produce_summary(slot):
    summary = {}
    for key, value in slot.items():
        if key.startswith("Child") and type(value) is list:
            # if "User" in key or "Group" in key:
            if any(x in key for x in ["User", "Group", "Owner"]):
                summary[key] = value
                continue
            summary[key + '_summary'] = sum(value)
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
    ]
    slots_info = collector.query(htcondor.AdTypes.Startd)
    result = []
    for slot in slots_info:
        info = {name: _process_slot_ad(slot, name) for name in projection}
        info =_produce_summary(info)
        result.append(info)
    
    return _slots_info_to_df(result)


# collector_address = "htc01.dice.priv:9618"
# collector = htcondor.Collector(collector_address)
# print(collector, dir(collector))
# schedulers = get_all_submitters(collector)
# print(schedulers)

# for schedd in schedulers:
#     print(schedd, dir(schedd))
#     break

# projection = ["Name", "MyAddress"]
# all_submitters_query = collector.query(htcondor.AdTypes.Collector, projection=projection)
# print(all_submitters_query)
# schedds = [htcondor.Schedd(submitter) for submitter in all_submitters_query]

# projection = ["Machine", "State", "Name", "SlotID", "Activity", "MyAddress"]
# all_submitters_query = collector.query(htcondor.AdTypes.Startd, projection=projection)
# slots_info = all_submitters_query
# for slot in slots_info:
#     name = slot.get("Machine", None)
#     slot_id = slot.get("SlotID", None)
#     activity = slot.get("Activity", None)
#     state = slot.get("State", None)
#     address = slot.get("MyAddress", "")
#     print(name, slot_id, activity, state, address)
# what do I want?
# 1. A ta
