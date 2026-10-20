import streamlit as st

#wide layout for every page, set once before the navigation
st.set_page_config(layout="wide")

pages = [
    st.Page("views/1_home.py", title="Home"),
    st.Page("views/2_table.py", title="Data table"),
    st.Page("views/3_plot.py", title="Plot"),
    st.Page("views/4_flows.py", title="Cross-border flows"),
    st.Page("views/5_latest_week.py", title="Latest week"),
]

menu = st.navigation(pages)
menu.run()
