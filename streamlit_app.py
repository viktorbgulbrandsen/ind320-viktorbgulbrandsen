import sys
from pathlib import Path

import streamlit as st

#streamlit.app runs this file, so it has to stay at the root. the live part is in project2/
PROJECT = Path(__file__).parent / "project2"
sys.path.insert(0, str(PROJECT))

#wide layout for every page, set once before the navigation
st.set_page_config(layout="wide")

pages = [
    st.Page(str(PROJECT / "views/1_home.py"), title="Home"),
    st.Page(str(PROJECT / "views/2_table.py"), title="Data table"),
    st.Page(str(PROJECT / "views/3_plot.py"), title="Plot"),
    st.Page(str(PROJECT / "views/4_flows.py"), title="Cross-border flows"),
    st.Page(str(PROJECT / "views/5_latest_week.py"), title="Latest week"),
]

menu = st.navigation(pages)
menu.run()
