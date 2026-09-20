import streamlit as st

pages = [
    st.Page("pages/1_home.py", title="Home"),
    st.Page("pages/2_table.py", title="Data table"),
    st.Page("pages/3_plot.py", title="Plot"),
]

menu = st.navigation(pages)
menu.run()
