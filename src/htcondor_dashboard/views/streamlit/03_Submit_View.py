from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

import htcondor_dashboard.condor as htc


def generate_submit_overview(display_grid, submit_info):
    result = []
    for schedd_name, job_info in submit_info.items():
        _, job_summary = job_info
        job_summary["Name"] = schedd_name
        result.append(job_summary)
    submit_info = pd.DataFrame.from_records(result)
    submit_info = submit_info.sort_values(by="Name")
    column_order = [
        "Name",
        "Jobs IDLE",
        "Jobs RUNNING",
        "Jobs HELD",
        "Jobs COMPLETED",
    ]
    display_grid.dataframe(submit_info, hide_index=True, column_order=column_order)


def generate_detailed_view(display_grid, submit_info):
    column_order = [
        "Owner",
        # "ExitStatus",
        "Cmd",
        "ClusterId",
        # "ProcId",
        # "GlobalJobId",
        "JobStatus",
        # "RemoteSlotID",
        "RemoteHost",
    ]
    status_order = ["IDLE", "RUNNING", "HELD", "COMPLETED"]
    for submit_node, (job_info, _) in submit_info.items():
        if len(job_info) == 0:
            continue
        display_grid.markdown(f"## {submit_node}")
        display_grid.markdown("### Summary")
        columns = st.columns(len(status_order))
        for i, status in enumerate(status_order):
            job_info_by_status = job_info[job_info["JobStatus"] == status]
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

        # sort jobs by status, running first
        display_grid.markdown("### Details")
        sorted_job_info = job_info.sort_values(
            by="JobStatus", key=lambda x: x == "RUNNING", ascending=False
        )
        display_grid.dataframe(
            sorted_job_info,
            hide_index=True,
            column_order=column_order,
            use_container_width=True,
        )


st.cache_data(ttl=60)


def generate_submit_view():
    submit_info = htc.get_submit_info()
    st.markdown("## Overview")
    generate_submit_overview(st, submit_info)
    generate_detailed_view(st, submit_info)


generate_submit_view()
