from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

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

def generate_submit_overview(display_grid, submit_info):
    submit_info = htc.get_submit_info()
    display_grid.markdown("## Submit Nodes")
    column_order = [
        "Name",
        "Jobs IDLE",
        "Jobs RUNNING",
        "Jobs HELD",
        "Jobs COMPLETED",
    ]
    display_grid.dataframe(submit_info, hide_index=True, column_order=column_order)

def generate_job_overview(display_grid, submit_info):
    """ Things to show:
    - Total jobs in the system
    - Running jobs
    - load avg compared to requested CPUs
    """
    display_grid.markdown("## Job statistics")
    status_order = ["IDLE", "RUNNING", "HELD", "COMPLETED"]
    all_jobs = pd.concat([job_info for job_info, _ in submit_info.values()])
    columns = st.columns(len(status_order))
    for i, status in enumerate(status_order):
            job_info_by_status = all_jobs[all_jobs["JobStatus"] == status]
            pie_chart = px.pie(
                job_info_by_status,
                names="Owner",
                title=f"{status} jobs",
                color="Owner",
                hole=0.3,
            )
            if len(job_info_by_status) == 0:
                pie_chart.update_traces(textinfo="none")
                pie_chart.add_annotation(text="No jobs", showarrow=False)
            columns[i].plotly_chart(pie_chart, use_container_width=True)


def generate_share_overview(display_grid):
    display_grid.markdown("## Share Overview 🚧")
    display_grid.dataframe(pd.DataFrame.from_records([{
        "group": "example1",
        "configured cluster share": 10,
        "current share": 5,
        "historical share": 7,
    },
    {
        "group": "example2",
        "configured cluster share": 20,
        "current share": 15,
        "historical share": 17,
    },
    {
        "group": "example3",
        "configured cluster share": 30,
        "current share": 25,
        "historical share": 27,
    }
    ]), hide_index=True)


def generate_status_view():
    # display_grid = grid(1, vertical_align="bottom")
    display_grid = st
    submit_info = htc.get_submit_info()

    generate_cluster_overview(display_grid)
    generate_submit_overview(display_grid, submit_info)
    generate_job_overview(display_grid, submit_info)
    generate_share_overview(display_grid, submit_info)


generate_status_view()
