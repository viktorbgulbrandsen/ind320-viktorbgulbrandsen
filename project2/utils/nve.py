import pandas as pd
import requests

API = "https://biapi.nve.no/magasinstatistikk/api/Magasinstatistikk"

#translate to english
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

#get relevant properties
SERIES = [
    "fill_level",
    "capacity_TWh",
    "fill_TWh",
    "fill_level_prev_week",
    "fill_level_change",
]


#whole history, the endpoint has no date parameters
def fetch_reservoirs():
    response = requests.get(f"{API}/HentOffentligData")
    response.raise_for_status()
    df = pd.DataFrame(response.json())

    #dates come as text. drop publiseringsdato, rename
    df["dato_Id"] = pd.to_datetime(df["dato_Id"])
    df = df.drop(columns="neste_Publiseringsdato")
    df = df.rename(columns=COLUMNS)

    #rows come in random order. sort by date, fix index
    df = df.sort_values("date")
    return df.reset_index(drop=True)


#the list of areas, one table
def fetch_areas():
    response = requests.get(f"{API}/HentOmråder")
    response.raise_for_status()
    areas = response.json()

    table = pd.DataFrame()
    for group in areas[0]:
        table = pd.concat([table, pd.DataFrame(areas[0][group])])

    table = table.reset_index(drop=True)
    return table[["omrType", "omrnr", "navn", "beskrivelse"]]
