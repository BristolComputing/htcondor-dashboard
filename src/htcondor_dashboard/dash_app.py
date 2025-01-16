from __future__ import annotations

import datetime

import pandas as pd
from dash import Dash, dash_table, html

import htcondor_dashboard.condor as htc

app = Dash(__name__)

gapminder_df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv"
)
gapminder_df = gapminder_df[["continent", "country", "pop", "lifeExp"]]  # prune columns for example
gapminder_df["Mock Date"] = [
    datetime.datetime(2020, 1, 1, 0, 0, 0) + i * datetime.timedelta(hours=13)
    for i in range(len(gapminder_df))
]

slot_df = htc.get_slots_info()
# drop child columns
slot_df = slot_df.drop(columns=[col for col in slot_df.columns if "Child" in col])

app.layout = [
    html.H1(children="Title of Dash App", style={"textAlign": "center"}),
    dash_table.DataTable(
        slot_df.to_dict("records"), [{"name": i, "id": i} for i in slot_df.columns]
    ),
]

if __name__ == "__main__":
    app.run_server(debug=True)
