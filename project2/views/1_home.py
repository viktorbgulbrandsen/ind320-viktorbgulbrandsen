import streamlit as st

st.title("Norwegian reservoir levels and cross-border flows")

st.write("This app looks at how full the Norwegian hydropower reservoirs are, week by week from 1995 to 2026.")
st.write("The reservoir data is fetched live from the NVE Magasinstatistikk API.")
st.write("The page on cross-border flows shows electricity flows between Norway and its neighbours.")
st.write("The flows go ENTSO-E API → Cassandra via Spark → MongoDB, which the app reads.")
st.write("Use the menu on the left to switch between pages.")
