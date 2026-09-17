#import pandas, streamlit
import pandas as pd
import streamlit as st

#get data
from reservoirs import load_reservoirs, national

#set heading
st.title("Data table")

#load data, national total only
df = load_reservoirs()
series = national(df)

#first month = the weeks in the same month as the first row
first_week = series.index[0]
first_month = series.loc[first_week.strftime("%Y-%m")]

#one list of values per column, for the line chart
sparklines = []
for column in first_month.columns:
    sparklines.append(first_month[column].tolist())

#one row per column
table = pd.DataFrame({"Column": first_month.columns, "First month": sparklines})

#write caption
first_day = first_month.index[0].date()
last_day = first_month.index[-1].date()
st.write(f"National total, weeks {first_day} to {last_day}.")

#show table, each chart scales to its own min and max
column_config = {"First month": st.column_config.LineChartColumn("First month (weekly)")}
st.dataframe(table, column_config=column_config, hide_index=True)
