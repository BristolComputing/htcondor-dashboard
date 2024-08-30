import streamlit as st
from streamlit_extras.grid import grid
import pandas as pd

import htcondor_dashboard.condor as htc


## Status page
# 1. Used + free resources (CPU, RAM, GPU)
# 2. Current jobs in the system
# 3. Submit nodes that are up
# 4. Share distribution (current + historical)

def generate_cluster_overview(display_grid):
    slot_info = htc.get_slots_info()
    overview = {
        "Nodes online": len(slot_info),
        "Jobs running": sum(slot_info["Jobs"]),
        "Total CPUs": sum(slot_info["CPUs"]),
        "Total GPUs": sum(slot_info["GPUs"]),
        "Total RAM [GB]": sum(slot_info["RAM"]) // 1024,
        "CPUs (available)": sum(slot_info["CPUs"]) - sum(slot_info["CPUs (Used)"]),
        "GPUs (available)": sum(slot_info["GPUs"]) - sum(slot_info["GPUs (Used)"]),
        "RAM [GB] (available)": sum(slot_info["RAM"]) // 1024 - sum(slot_info["RAM (Used)"]) // 1024,
        
        # "Total GPUs": sum(slot["TotalSlotGPUs"] for slot in slot_info),
        # "Total RAM [GB]": sum(slot["TotalSlotMemory"] for slot in slot_info) // 1024,
        # "Total Disk [GB]": sum(slot["TotalSlotDisk"] for slot in slot_info) // 1024 // 1024,
    }
    df_overview = pd.DataFrame.from_records([overview])
    display_grid.markdown("## Resources")
    display_grid.dataframe(df_overview, hide_index=True)

def generate_submit_overview(display_grid):
    submit_names = htc.get_submit_names()
    df_names = pd.DataFrame(submit_names, columns=["Name"])
    display_grid.markdown("## Submit Nodes")
    display_grid.dataframe(df_names, hide_index=True)

def generate_job_overview(display_grid):
    """ Things to show:
    - Total jobs in the system
    - Running jobs
    - load avg compared to requested CPUs
    """
    display_grid.markdown("## Job statistics")

def generate_share_overview(display_grid):
    display_grid.markdown("## Share Overview")


def generate_status_view():
    display_grid = grid(1, vertical_align="bottom")

    generate_cluster_overview(display_grid)
    generate_submit_overview(display_grid)
    generate_job_overview(display_grid)
    generate_share_overview(display_grid)


generate_status_view()
# my_grid = grid(1, vertical_align="bottom")

# generate_submit_overview(my_grid)


# slot_info = htc.get_slots_info()
# # create DF from slot_info
# df = pd.DataFrame.from_records(slot_info).sort_values(by="Machine")
# df.to_csv("slot_info.csv", index=False)
# df["Status"] = df["Start"]
# df = df[df["Name"].str.startswith("slot1@")]
# df["OS"] = df["OpSysAndVer"] + "/" + df["Microarch"]
# # my_grid.dataframe(df, hide_index=True, use_container_width=True)

# df["Jobs"] = df["NumDynamicSlots"]
# df["CPUs"] = df["TotalSlotCpus"]
# df["CPUs (Used)"] = df["ChildCpus_summary"]
# df["GPUs"] = df["TotalSlotGPUs"]
# df["GPUs (Used)"] = df["ChildGPUs_summary"]
# df["RAM [GB]"] = df["TotalSlotMemory"] // 1024
# df["RAM [GB] (Used)"] = (df["ChildMemory_summary"]) // 1024
# df["Disk [GB]"] = df["TotalSlotDisk"] // 1024 // 1024
# df["Disk [MB] (Used)"] = df["ChildDisk_summary"] // 1024
# column_order = [
#     "Machine",
#     "Status",
#     "OS",
#     "Jobs",
#     "TotalLoadAvg",
#     "CPUs",
#     "CPUs (Used)",
#     "GPUs",
#     "GPUs (Used)",
#     "RAM [GB]",
#     "RAM [GB] (Used)",
#     "Disk [GB]",
#     "Disk [MB] (Used)",
# ]
# my_grid.markdown("## Node Summary")
# my_grid.dataframe(df, column_order=column_order, hide_index=True)
