#import pandas, plotly, streamlit
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

#get data
from utils.nve import NAMES, PERCENT, SERIES, fetch_areas, fetch_reservoirs


#wrap like conventionally
@st.cache_data
def get_reservoirs():
    return fetch_reservoirs()


@st.cache_data
def get_areas():
    return fetch_areas()


#set heading
st.title("Plot")

#load data, all areas
df = get_reservoirs()
areas = get_areas()

#pick the type of area and one column
area_type = st.radio("Area type", ["EL", "NO", "VASS"], horizontal=True)
st.caption("EL = price areas NO1 to NO5, NO = whole country, VASS = water regions.")
choice = st.selectbox("Column", SERIES, format_func=NAMES.get)

#weekly dates to months, one label per month
month = df["date"].dt.to_period("M")
months = []
for period in month.unique():
    months.append(str(period))

#slider over months, starts on the last five years
start, end = st.select_slider("Months to show", options=months, value=(months[-60], months[-1]))

#the endpoint has no date parameters, so the interval is the rows kept after the fetch
after_start = month >= pd.Period(start)
before_end = month <= pd.Period(end)
subset = df[after_start & before_end & (df["area_type"] == area_type)]

#names of the areas of this type
chosen = areas[areas["omrType"] == area_type]

#one line per area number
fig = go.Figure()
for area_no in sorted(subset["area_no"].unique()):
    one = subset[subset["area_no"] == area_no]
    name = chosen[chosen["omrnr"] == area_no]["navn"].iloc[0]
    values = one[choice]
    if choice in PERCENT:
        values = values * 100
    fig.add_trace(go.Scatter(x=one["date"], y=values, name=name))

#title and axis labels
fig.update_layout(title=f"Reservoirs by area ({area_type}), {start} to {end}", xaxis_title="Date", yaxis_title=NAMES[choice], legend_title="Area")

#show
st.plotly_chart(fig)
