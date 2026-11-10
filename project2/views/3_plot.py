#import pandas, plotly, streamlit
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from plotly.subplots import make_subplots

#get data
from utils.nve import NAMES, PERCENT, SERIES, fetch_areas, fetch_reservoirs


#one colour per area from the standard plotly colours
COLORS = px.colors.qualitative.Plotly

#extra choice in the column box
ALL = "All columns"


#wrap like conventionally
@st.cache_data
def get_reservoirs():
    return fetch_reservoirs()


@st.cache_data
def get_areas():
    return fetch_areas()


#readable name for the column box
def column_name(name):
    if name == ALL:
        return name
    return NAMES[name]


#set heading
st.title("Plot")

#load data, all areas
df = get_reservoirs()
areas = get_areas()

#pick the type of area and one column
area_type = st.radio("Area type", ["EL", "NO", "VASS"], horizontal=True)
st.caption("EL = price areas NO1 to NO5, NO = whole country, VASS = water regions.")
choice = st.selectbox("Column", [*SERIES, ALL], format_func=column_name)

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

#one column or every column in its own panel
#the units differ so they cannot share one
columns = SERIES if choice == ALL else [choice]
fig = make_subplots(rows=len(columns), cols=1, shared_xaxes=True, subplot_titles=[NAMES[name] for name in columns])

#one line per area number in every panel
#an area keeps its colour in all panels
for row, name in enumerate(columns, start=1):
    for number, area_no in enumerate(sorted(subset["area_no"].unique())):
        one = subset[subset["area_no"] == area_no]
        area = chosen[chosen["omrnr"] == area_no]["navn"].iloc[0]
        values = one[name]
        if name in PERCENT:
            values = values * 100
        color = COLORS[number % len(COLORS)]
        #the legend lists each area once
        first_panel = row == 1
        line = {"color": color}
        trace = go.Scatter(x=one["date"], y=values, name=area, legendgroup=area, showlegend=first_panel, line=line)
        fig.add_trace(trace, row=row, col=1)

#title and axis label and a height that grows with the number of panels
fig.update_layout(title=f"Reservoirs by area ({area_type}), {start} to {end}", legend_title="Area", height=350 * len(columns))
fig.update_xaxes(title_text="Date", row=len(columns), col=1)
if choice != ALL:
    fig.update_yaxes(title_text=NAMES[choice])

#show
st.plotly_chart(fig)
