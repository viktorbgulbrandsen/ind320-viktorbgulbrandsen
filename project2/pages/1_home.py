import streamlit as st

st.title("Norwegian reservoir levels and cross-border flows")

st.write("This app looks at how full the Norwegian hydropower reservoirs are, week by week from 1995 to 2026.")
st.write("The reservoir data is fetched live from the NVE Magasinstatistikk API.")
st.write("The page on cross-border flows reads electricity flows between Norway and its neighbours from a MongoDB database.")
st.write("Use the menu on the left to switch between pages.")
