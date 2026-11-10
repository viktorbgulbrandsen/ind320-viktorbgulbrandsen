#import streamlit
import streamlit as st

#get reservoir data and weather and the two analyses
from utils.mongo import get_client
from utils.nve import fetch_reservoirs
from utils.quality import lof_anomalies, spc_outliers
from utils.weather import area_weather

#the area types of magasinstatistikk
#same radio as on the data table page
TYPES = ["EL", "NO", "VASS"]

#the year the weather is shown for
#same year as in the notebook
YEAR = 2024


#wrap like conventionally
@st.cache_data
def get_reservoirs():
    return fetch_reservoirs()


#one client for the whole app
@st.cache_resource
def connect():
    return get_client()


#hourly weather of one area from mongodb
#it is the mean over the 50 points
@st.cache_data(show_spinner="Getting the weather. A new area is downloaded from open-meteo the first time, about 10 seconds.")
def get_weather(region):
    return area_weather(connect()["ind320"]["weather"], region, YEAR)


#area code like the weather files use
#no1 and vass1 and just no for the country
def region_key(area_type, area_no):
    if area_type == "EL":
        return f"NO{area_no}"
    if area_type == "VASS":
        return f"VASS{area_no}"
    return "NO"


#no alone is the whole country
def label(region):
    if region == "NO":
        return "Norway"
    return region


#set heading
st.title("Weather outliers")
st.write(f"Hourly ERA5 weather from open-meteo for {YEAR}, averaged over 50 random points in the area.")

#load data to offer the same areas as the reservoir pages
df = get_reservoirs()

#the area choice carries over to the decomposition page and back
#no3 is the area the notebook works with
st.session_state.setdefault("area_type", "EL")
st.session_state.setdefault("region", "NO3")

#pick the type of area like on the data table page
area_type = st.radio("Area type", TYPES, index=TYPES.index(st.session_state["area_type"]), horizontal=True)
st.session_state["area_type"] = area_type
st.caption("EL = price areas NO1 to NO5, NO = whole country, VASS = water regions.")

#then one area of that type
#only the ones that have reservoir data
numbers = sorted(df[df["area_type"] == area_type]["area_no"].unique())
options = []
for area_no in numbers:
    options.append(region_key(area_type, area_no))
saved = st.session_state["region"]
if saved not in options:
    saved = options[0]
region = st.pills("Area", options, default=saved, format_func=label)

#pills can be clicked off and then there is nothing to show
if region is None:
    st.info("Pick an area.")
    st.stop()
st.session_state["region"] = region

weather = get_weather(region)

spc_tab, lof_tab = st.tabs(["Outliers (SPC)", "Anomalies (LOF)"])

with spc_tab:
    left, right = st.columns(2)

    #dct cutoff in cycles per year
    #slower variation is filtered away
    with left:
        cutoff = st.slider("DCT cut-off (cycles per year)", min_value=1, max_value=365, value=12)

    #robust standard deviations from the centre before a value is an outlier
    with right:
        n_std = st.slider("Number of standard deviations", min_value=1.0, max_value=6.0, value=3.0, step=0.5)

    #the name of the series is the label in the plot
    #two charts on one page need their own key
    precipitation = weather["precipitation"].rename("Precipitation (mm)")
    fig, summary = spc_outliers(precipitation, cutoff=cutoff, n_std=n_std)
    st.plotly_chart(fig, key="spc")

    #how many hours were flagged and how wide the band is
    first, second, third = st.columns(3)
    first.metric("Outliers", summary["n_outliers"])
    second.metric("Share of hours", f"{summary['share'] * 100:.2f} %")
    low, high = summary["limits"]
    third.metric("Band around the slow part (mm)", f"{low:.2f} to {high:.2f}")

    #the flagged hours with readable column names
    table = summary["outliers"].rename(columns={"time": "Time (UTC)", "value": "Precipitation (mm)"})
    st.dataframe(table, hide_index=True)

with lof_tab:
    #expected share of anomalies
    #the task asks for 1 % as default
    contamination = st.slider("Proportion of outliers (%)", min_value=0.1, max_value=10.0, value=1.0, step=0.1) / 100

    temperature = weather["temperature_2m"].rename("Temperature (°C)")
    fig, summary = lof_anomalies(temperature, contamination=contamination)
    st.plotly_chart(fig, key="lof")

    #how many hours were flagged
    first, second = st.columns(2)
    first.metric("Anomalies", summary["n_anomalies"])
    second.metric("Share of hours", f"{summary['share'] * 100:.2f} %")

    #the flagged hours with readable column names
    table = summary["anomalies"].rename(columns={"time": "Time (UTC)", "value": "Temperature (°C)", "lof": "LOF score"})
    st.dataframe(table, hide_index=True)
