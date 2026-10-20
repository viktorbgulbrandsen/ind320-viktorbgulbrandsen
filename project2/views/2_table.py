#import pandas, streamlit
import pandas as pd
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
st.title("Data table")

#load data, all areas
df = get_reservoirs()
areas = get_areas()

#pick the type of area
area_type = st.radio("Area type", ["EL", "NO", "VASS"], horizontal=True)
st.caption("EL = price areas NO1 to NO5, NO = whole country, VASS = water regions.")

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

#one row per area, one list of values per column for the line charts
rows = []
for area_no in sorted(subset["area_no"].unique()):
    one = subset[subset["area_no"] == area_no]
    name = chosen[chosen["omrnr"] == area_no]["navn"].iloc[0]
    row = {"Area": name}
    for column in SERIES:
        values = one[column]
        if column in PERCENT:
            values = values * 100
        row[NAMES[column]] = values.tolist()
    #capacity does not change, so one number instead of a flat line
    row[NAMES["capacity_TWh"]] = one["capacity_TWh"].iloc[-1]
    rows.append(row)
table = pd.DataFrame(rows)

#write caption
st.write(f"Weekly values, {start} to {end}.")

#show table, each chart scales to its own min and max
column_config = {NAMES["capacity_TWh"]: st.column_config.NumberColumn(format="%.1f")}
for column in SERIES:
    if column != "capacity_TWh":
        column_config[NAMES[column]] = st.column_config.LineChartColumn(NAMES[column])
st.dataframe(table, column_config=column_config, hide_index=True)
