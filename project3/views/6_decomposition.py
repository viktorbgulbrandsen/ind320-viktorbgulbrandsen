#import streamlit
import streamlit as st

#get data and the two analyses of the fill level
from utils.nve import fetch_reservoirs
from utils.quality import spectrogram_plot, stl_plot

#the area types of magasinstatistikk
#same radio as on the data table page
TYPES = ["EL", "NO", "VASS"]


#wrap like conventionally
@st.cache_data
def get_reservoirs():
    return fetch_reservoirs()


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
st.title("Fill level decomposition")
st.write("The weekly reservoir fill level of one area, split into trend, season and remainder (STL), and as a spectrogram.")

#load data for all areas
df = get_reservoirs()

#the area choice carries over to the weather page and back
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

#one weekly series for the chosen area with dates as index
#the name is the label in the plots
area_no = numbers[options.index(region)]
one = df[(df["area_type"] == area_type) & (df["area_no"] == area_no)]
series = one.set_index("date")["fill_level"].rename("Fill level (share, 0 to 1)")

stl_tab, spectrogram_tab = st.tabs(["STL", "Spectrogram"])

with stl_tab:
    left, middle, right = st.columns(3)

    #seasonal smoother must be odd and at least 3
    with left:
        seasonal = st.slider("Seasonal smoother (odd)", min_value=3, max_value=105, value=13, step=2)

    #trend smoother must be odd and longer than a year
    with middle:
        trend = st.slider("Trend smoother (weeks, odd)", min_value=53, max_value=261, value=105, step=2)

    #robust fit gives single odd weeks less weight
    with right:
        robust = st.toggle("Robust", value=False)

    #two charts on one page need their own key
    fig = stl_plot(series, seasonal=seasonal, trend=trend, robust=robust)
    st.plotly_chart(fig, key="stl")

with spectrogram_tab:
    left, right = st.columns(2)

    #window length in weeks
    #longer sharpens frequency and blurs time
    with left:
        window_length = st.slider("Window length (weeks)", min_value=16, max_value=260, value=104, step=4)

    #overlap in weeks must stay below the window length
    with right:
        overlap = st.slider("Window overlap (weeks)", min_value=0, max_value=window_length - 2, value=min(78, window_length - 2), step=2)

    fig = spectrogram_plot(series, window_length=window_length, overlap=overlap)
    st.plotly_chart(fig, key="spectrogram")
