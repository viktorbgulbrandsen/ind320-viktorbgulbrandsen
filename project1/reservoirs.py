#import path
from pathlib import Path

#import needed modules
import pandas as pd
import streamlit as st

# set correct path
CSV = Path(__file__).parent / "data" / "reservoirs.csv"

#translate to norwegian
COLUMNS = {
    "dato_Id": "date",
    "omrType": "area_type",
    "omrnr": "area_no",
    "iso_aar": "iso_year",
    "iso_uke": "iso_week",
    "fyllingsgrad": "fill_level",
    "kapasitet_TWh": "capacity_TWh",
    "fylling_TWh": "fill_TWh",
    "fyllingsgrad_forrige_uke": "fill_level_prev_week",
    "endring_fyllingsgrad": "fill_level_change",
}

# get relevant properties
SERIES = [
    "fill_level",
    "capacity_TWh",
    "fill_TWh",
    "fill_level_prev_week",
    "fill_level_change",
]


# wrap like conventionally
@st.cache_data
def load_reservoirs():
    #read with pandas. drop publiseringsdato
    df = pd.read_csv(CSV, parse_dates=["dato_Id"])
    df = df.drop(columns="neste_Publiseringsdato")
    df = df.rename(columns=COLUMNS)
    # sort by date, fix index
    df = df.sort_values("date")
    return df.reset_index(drop=True)


#national total only, date as index
def national(df):
    df = df[df["area_type"] == "NO"]
    df = df.set_index("date")
    return df[SERIES]
