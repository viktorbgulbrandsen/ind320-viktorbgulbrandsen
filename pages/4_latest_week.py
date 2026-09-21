#import plotly, streamlit
import plotly.express as px
import streamlit as st

#get data
from reservoirs import load_reservoirs

#set heading
st.title("Latest week")

#load data, all areas this time
df = load_reservoirs()

#keep only the last week
last_date = df["date"].max()
latest = df[df["date"] == last_date]
latest = latest.sort_values(["area_type", "area_no"])

#area codes to readable names
labels = []
for area_type, area_no in zip(latest["area_type"], latest["area_no"]):
    if area_type == "NO":
        labels.append("Norway")
    elif area_type == "EL":
        labels.append(f"NO{area_no}")
    else:
        labels.append(f"Water region {area_no}")

#write caption
st.write(f"Fill level per area in the week of {last_date.date()}.")

#one bar per area, y from 0 to 1
fig = px.bar(x=labels, y=latest["fill_level"], labels={"x": "Area", "y": "Share of capacity"}, title="Reservoir fill level by area")
fig.update_yaxes(range=[0, 1])

#show
st.plotly_chart(fig)
