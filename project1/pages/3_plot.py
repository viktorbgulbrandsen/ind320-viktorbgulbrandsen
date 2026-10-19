#import pandas, plotly, streamlit
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

#get data
from reservoirs import SERIES, load_reservoirs, national

#set heading
st.title("Plot")

#load data, national total only
df = load_reservoirs()
series = national(df)

#pick one column or all
choice = st.selectbox("Column", ["All columns"] + SERIES)

#weekly dates to months, one label per month
month = series.index.to_period("M")
months = []
for period in month.unique():
    months.append(str(period))

#slider over months, starts on the first month
start, end = st.select_slider("Months", options=months, value=(months[0], months[0]))

#keep the weeks between start and end
after_start = month >= pd.Period(start)
before_end = month <= pd.Period(end)
subset = series[after_start & before_end]

#two y-axes, share of capacity left and TWh right
fig = make_subplots(specs=[[{"secondary_y": True}]])

#all columns or just the chosen one
if choice == "All columns":
    columns = SERIES
else:
    columns = [choice]

#TWh columns go on the right axis
for column in columns:
    line = go.Scatter(x=subset.index, y=subset[column], name=column)
    fig.add_trace(line, secondary_y=column.endswith("TWh"))

#title and axis labels
fig.update_layout(title=f"National reservoirs, {start} to {end}", xaxis_title="Date")
fig.update_yaxes(title_text="Share of capacity", secondary_y=False)
fig.update_yaxes(title_text="TWh", secondary_y=True)

#show
st.plotly_chart(fig)
