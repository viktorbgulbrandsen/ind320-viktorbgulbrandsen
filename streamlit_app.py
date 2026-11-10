import sys
from pathlib import Path

import streamlit as st

#streamlit.app runs this file so it has to stay at the root
#part 2 and part 3 both live in the app
PART2 = Path(__file__).parent / "project2"
PART3 = Path(__file__).parent / "project3"

#project3 goes first
#its utils package also reaches the files of project2/utils
#so utils.nve and utils.mongo and utils.quality all import
sys.path.insert(0, str(PART2))
sys.path.insert(0, str(PART3))

#wide layout for every page
#set once before the navigation
st.set_page_config(layout="wide")

#one flat menu
#the reservoir pages come first then weather then the power flows
pages = [
    st.Page(str(PART2 / "views/1_home.py"), title="Home"),
    st.Page(str(PART2 / "views/5_latest_week.py"), title="Latest week"),
    st.Page(str(PART2 / "views/2_table.py"), title="Data table"),
    st.Page(str(PART2 / "views/3_plot.py"), title="Plot"),
    st.Page(str(PART3 / "views/6_decomposition.py"), title="Fill level decomposition"),
    st.Page(str(PART3 / "views/7_outliers.py"), title="Weather outliers"),
    st.Page(str(PART2 / "views/4_flows.py"), title="Cross-border flows"),
]

menu = st.navigation(pages)
menu.run()
