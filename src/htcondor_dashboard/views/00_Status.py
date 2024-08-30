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
    }
    df_overview = pd.DataFrame.from_records([overview])
    display_grid.markdown("## Resources")
    display_grid.dataframe(df_overview, hide_index=True)

def generate_submit_overview(display_grid):
    submit_info = htc.get_submit_info()
    result = []
    for schedd_name, job_info in submit_info.items():
        _, job_summary = job_info
        job_summary['Name'] = schedd_name
        result.append(job_summary)
    submit_info = pd.DataFrame.from_records(result)
    submit_info = submit_info.sort_values(by="Name")
    display_grid.markdown("## Submit Nodes")
    column_order = [
        "Name",
        "Jobs IDLE",
        "Jobs RUNNING",
        "Jobs HELD",
        "Jobs COMPLETED",
    ]
    display_grid.dataframe(submit_info, hide_index=True, column_order=column_order)

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
