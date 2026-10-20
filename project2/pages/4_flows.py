#import plotly, streamlit
import plotly.express as px
import streamlit as st

#get data
from utils.mongo import get_client, list_connections, load_flows

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

    fig = px.pie(values=totals.values, names=totals.index, title=f"{connection} {year}, GWh in and out of Norway")
    st.plotly_chart(fig)

with right:
    #pick months, january to start with
    picked = st.pills("Months", MONTHS, selection_mode="multi", default=["Jan"])

    #month names to numbers
    numbers = []
    for name in picked:
        numbers.append(MONTHS.index(name) + 1)

    #one line per direction
    chosen = one[one["time"].dt.month.isin(numbers)]
    if len(chosen) == 0:
        st.info("No data for the chosen months.")
    else:
        fig = px.line(chosen, x="time", y="quantity", color="direction", title=f"{connection} {year}, MW")
        st.plotly_chart(fig)

#document the source
with st.expander("About the data"):
    st.write("The flows are the physical cross-border flows between Norway and its neighbours, in MW, from the ENTSO-E transparency platform.")
    st.write("They were fetched from the ENTSO-E API for the last two years, stored in Cassandra with Spark, and the extracted columns were then inserted into MongoDB, which this page reads.")
    st.write("Export is the flow out of Norway and import the flow into Norway.")
