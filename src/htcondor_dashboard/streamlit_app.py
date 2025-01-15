import streamlit as st
from itertools import islice

st.set_page_config(
    page_title="HTCondor Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)
# st.header("HTCondor Dashboard")

status_page = st.Page("views/00_Status.py", title="Status", default=True)
job_view_page = st.Page("views/01_Job_View.py")
node_view_page = st.Page("views/02_Node_View.py")
schedd_view = st.Page("views/03_Submit_View.py")
historical_view = st.Page("views/09_Historical_View.py")
other_page = st.Page("views/99_Other.py")

pg = st.navigation([status_page, job_view_page, node_view_page, schedd_view, historical_view, other_page])
pg.run()

