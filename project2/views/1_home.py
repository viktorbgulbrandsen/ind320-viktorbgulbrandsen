import streamlit as st

st.title("Norwegian reservoirs, weather and cross-border flows")

st.write("This app looks at how full the Norwegian hydropower reservoirs are, week by week from 1995 to 2026.")
st.write("The reservoir data is fetched live from the NVE Magasinstatistikk API.")
st.write("The page on fill level decomposition splits the fill level of one area into trend and season, and shows it as a spectrogram.")
st.write("The page on weather outliers shows hourly precipitation and temperature for 2024 from the open-meteo API, and marks the hours that stand out.")
st.write("The page on cross-border flows shows electricity flows between Norway and its neighbours.")
st.write("The flows are fetched from the ENTSO-E API, written to Cassandra with Spark and then to MongoDB, which the app reads.")
st.write("Use the menu on the left to switch between pages.")
