from __future__ import annotations

from itertools import islice

import pandas as pd
from streamlit_extras.grid import grid

import htcondor_dashboard.condor as htc


def show_node(node, info, display_grid):
    display_grid.markdown(f"### {node}")
    column_order = [
        "FQDN",
        "Status",
        "OS",
        "Jobs",
        "TotalLoadAvg",
        "CPUs",
        "CPUs (Used)",
        "GPUs",
        "GPUs (Used)",
        "RAM [GB]",
        "RAM [GB] (Used)",
        "Disk [GB]",
        "Disk [MB] (Used)",
    ]
    display_grid.dataframe(info, hide_index=True, column_order=column_order)
    display_grid.markdown("#### Jobs")
    job_columns = [
        "ChildRemoteUser",
        "ChildAccountingGroup",
        "ChildCpus",
        "ChildGPUs",
        "ChildMemory",
        "ChildDisk",
    ]
    job_info = info[job_columns]
    job_info.loc[:, "ChildAccountingGroup"] = job_info["ChildAccountingGroup"].apply(
        lambda x: [str(i) for i in x]
    )
    job_info = job_info.apply(pd.Series.explode, ignore_index=True)
    display_grid.dataframe(job_info, hide_index=True, column_order=job_columns)


def batcher(iterable, batch_size):
    iterator = iter(iterable)
    while batch := list(islice(iterator, batch_size)):
        yield batch


def generate_node_summary(slot_info, display_grid):
    column_order = [
        "FQDN",
        "Status",
        "OS",
        "Jobs",
        "TotalLoadAvg",
        "CPUs",
        "CPUs (Used)",
        "GPUs",
        "GPUs (Used)",
        "RAM [GB]",
        "RAM [GB] (Used)",
        "Disk [GB]",
        "Disk [MB] (Used)",
        "Uptime [h]",
        "Idle Time [h]",
    ]
    display_grid.markdown("## Node Summary")
    display_grid.dataframe(slot_info, column_order=column_order, hide_index=True)


def generate_node_detail(slot_info, nodes, display_grid, batch_size=10):
    display_grid.markdown("## Node Detail (WIP)")
    batches = list(batcher(nodes, batch_size))
    max_batch_size = max([len(batch) for batch in batches])
    for batch in batches:
        # add padding of empty cells if batch is not full
        for node in batch:
            display_grid.button(
                str(node),
                on_click=show_node,
                args=(
                    node,
                    slot_info[slot_info["node"] == node],
                    display_grid,
                ),
            )
        for _ in range(max_batch_size - len(batch)):
            display_grid.write("")


def generate_node_view():
    # nodes = [f"hd{i:02d}" for i in range(91)]
    # slot_info = get_node_info()
    slot_info = htc.get_slots_info()
    # extract the host name and drop the domain
    nodes = slot_info["node"].to_list()

    # nodes = slot_info["Machine"].str.extract(r'^([^\.]+)').to_list()
    # nodes = slot_info["Machine"].str.extract(r'*.\.').tolist()

    display_grid = grid(
        1,  # section header 1
        1,  # summary table
        1,  # section header 2
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # node buttons (should come from batches)
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # node buttons (should come from batches)
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # node buttons (should come from batches)
        1,
        1,
        vertical_align="bottom",
    )
    generate_node_summary(slot_info, display_grid)
    generate_node_detail(slot_info, nodes, display_grid)


generate_node_view()
