#import plotly, streamlit
import plotly.express as px
import streamlit as st

#get data
from utils.nve import fetch_reservoirs


#wrap like conventionally
@st.cache_data
def get_reservoirs():
    return fetch_reservoirs()


#set heading
st.title("Latest week")

#load data, all areas
df = get_reservoirs()

#keep only the last week
last_date = df["date"].max()
latest = df[df["date"] == last_date]
latest = latest.sort_values(["area_type", "area_no"])

#area codes to readable names, and the kind of area for the colour
labels = []
kinds = []
for area_type, area_no in zip(latest["area_type"], latest["area_no"]):
    if area_type == "NO":
        labels.append("Norway")
        kinds.append("Whole country")
    elif area_type == "EL":
        labels.append(f"NO{area_no}")
        kinds.append("Price areas (NO1 to NO5)")
    else:
        labels.append(f"VASS{area_no}")
        kinds.append("Water regions (VASS)")

#write caption
st.write(f"Fill level per area in the week of {last_date.date()}.")

#one bar per area, coloured by kind of area, y from 0 to 100
names = {"x": "Area", "y": "Fill level (%)", "color": "Kind of area"}
fig = px.bar(x=labels, y=latest["fill_level"] * 100, color=kinds, labels=names, title="Reservoir fill level by area")
fig.update_yaxes(range=[0, 100])

#show
st.plotly_chart(fig)
