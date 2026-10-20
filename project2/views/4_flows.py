#import plotly, streamlit
import plotly.express as px
import streamlit as st

#get data
from utils.mongo import get_client, list_connections, load_flows

COLORS = {"export": "#EF553B", "import": "#636EFA"}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


#one client for the whole app
@st.cache_resource
def connect():
    return get_client()


#query only every ten minutes
@st.cache_data(ttl=600)
def get_connections():
    return list_connections(connect())


@st.cache_data(ttl=600)
def get_flows(connection):
    return load_flows(connect(), connection)


#set heading
st.title("Cross-border flows")

#stop if the collection is empty
connections = get_connections()
if len(connections) == 0:
    st.info("No flows in the database yet.")
    st.stop()

left, right = st.columns(2)

with left:
    #pick connection, then year from what that connection has
    connection = st.radio("Connection", connections)
    flows = get_flows(connection)
    years = sorted(flows["time"].dt.year.unique())
    year = st.selectbox("Year", years, index=len(years) - 1)

    #the data is MW, so hourly mean, sum to MWh, divide to GWh
    one = flows[flows["time"].dt.year == year]
    hourly = one.set_index("time").groupby("direction")["quantity"].resample("1h").mean()
    totals = hourly.groupby("direction").sum() / 1000

    fig = px.pie(values=totals.values, names=totals.index, color=totals.index, color_discrete_map=COLORS, title=f"{connection} {year}, GWh in and out of Norway")
    st.plotly_chart(fig)

with right:
    #pills do not wrap, so two rows of six
    first = st.pills("Months", MONTHS[:6], selection_mode="multi", default=["Jan"])
    second = st.pills("second half", MONTHS[6:], selection_mode="multi", label_visibility="collapsed")
    picked = first + second

    #month names to numbers
    numbers = []
    for name in picked:
        numbers.append(MONTHS.index(name) + 1)

    #daily means, hourly values over whole months are a solid wall
    chosen = one[one["time"].dt.month.isin(numbers)]
    if len(chosen) == 0:
        st.info("No data for the chosen months.")
    else:
        mean = chosen.set_index("time").groupby("direction")["quantity"].resample("1D").mean().reset_index()
        labels = {"time": "Date (UTC)", "quantity": "Flow (MW)", "direction": "Direction"}
        fig = px.line(mean, x="time", y="quantity", color="direction", color_discrete_map=COLORS, labels=labels, title=f"{connection} {year}, daily mean flow")
        st.plotly_chart(fig)

#document the source
with st.expander("About the data"):
    st.write("The flows are the physical cross-border flows between Norway and its neighbours, in MW, from the ENTSO-E transparency platform.")
    st.write("The flows go ENTSO-E API → Cassandra via Spark → MongoDB, which the app reads.")
    st.write("They cover the last two years, and the times are UTC.")
    st.write("Export is the flow out of Norway and import the flow into Norway.")
