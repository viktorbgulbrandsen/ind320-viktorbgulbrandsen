import sys
from pathlib import Path

import streamlit as st

# part 1 lives in project1/ and is left as it was handed in.
# its pages import `reservoirs`, so project1/ has to be on the path.
PART1 = Path(__file__).resolve().parent.parent / "project1"
sys.path.insert(0, str(PART1))

pages = [
    st.Page(str(PART1 / "pages/1_home.py"), title="Home"),
    st.Page(str(PART1 / "pages/2_table.py"), title="Data table"),
    st.Page(str(PART1 / "pages/3_plot.py"), title="Plot"),
    st.Page(str(PART1 / "pages/4_latest_week.py"), title="Latest week"),
]

menu = st.navigation(pages)
menu.run()
