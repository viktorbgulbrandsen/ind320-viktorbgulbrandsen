import json
from pathlib import Path

import pandas as pd
import requests

API = "https://archive-api.open-meteo.com/v1/archive"
DATA = Path(__file__).resolve().parents[1] / "data"

VARIABLES = [
    "precipitation",
    "temperature_2m",
    "rain",
    "snowfall",
    "relative_humidity_2m",
    "wind_speed_10m",
    "cloud_cover",
    "pressure_msl",
    "shortwave_radiation",
    "et0_fao_evapotranspiration",
]
#the app only needs these two
APP_VARIABLES = ["precipitation", "temperature_2m"]

#open-meteo counts a year for one point as about 26 calls
#the free limit is 600 calls a minute so 19 points fit in one request
BATCH = 19


def download(points, start, end, variables):
    params = {
        "latitude": ",".join(f"{lat:.5f}" for lat in points["lat"]),
        "longitude": ",".join(f"{lon:.5f}" for lon in points["lon"]),
        "start_date": start,
        "end_date": end,
        "models": "era5",
        "hourly": ",".join(variables),
        "timezone": "GMT",
        "timeformat": "unixtime",
        "wind_speed_unit": "ms",
    }
    response = requests.get(API, params=params)
    response.raise_for_status()

    #one point gives a dict and several give a list
    answer = response.json()
    if isinstance(answer, dict):
        answer = [answer]

    frames = []
    for location in answer:
        hourly = pd.DataFrame(location["hourly"])
        hourly["time"] = pd.to_datetime(hourly["time"], unit="s")
        frames.append(hourly)
    return frames


def point_file(lon, lat, start, end):
    return DATA / f"weather_{start}_{end}" / f"{lat:.5f}_{lon:.5f}.parquet"


#one row per point and hour for every point in the region
def fetch_weather(region, start, end):
    #regions needs geopandas which the app does not have
    #so it is imported here and not at the top
    from utils.regions import sample_points

    points = sample_points(region)
    files = [point_file(lon, lat, start, end) for lon, lat in zip(points["lon"], points["lat"])]

    #only the points that are not on disk yet are downloaded
    #each point gets its own file so a download that stops can go on later
    is_missing = [not file.exists() for file in files]
    missing = points[is_missing]
    for first in range(0, len(missing), BATCH):
        todo = missing.iloc[first:first + BATCH]
        frames = download(todo, start, end, VARIABLES)
        for lon, lat, hourly in zip(todo["lon"], todo["lat"], frames):
            file = point_file(lon, lat, start, end)
            file.parent.mkdir(parents=True, exist_ok=True)
            hourly.to_parquet(file, index=False)
        print(f"{region}: {first + len(todo)} of {len(missing)} missing points downloaded")

    table = []
    for lon, lat, file in zip(points["lon"], points["lat"], files):
        hourly = pd.read_parquet(file)
        hourly.insert(0, "lat", lat)
        hourly.insert(0, "lon", lon)
        table.append(hourly)
    return pd.concat(table, ignore_index=True)


def region_mean(df):
    df = df.drop(columns=["lon", "lat"])
    means = df.groupby("time").mean()
    #asfreq makes sure there is a row for every hour
    means = means.asfreq("h")
    return means.reset_index()


#the app uses the first 50 of the 1000 points
def app_points(region):
    with open(DATA / "points_50.json") as file:
        points = json.load(file)[region]
    return pd.DataFrame(points, columns=["lon", "lat"])


def download_area(region, year):
    points = app_points(region)
    frames = download(points, f"{year}-01-01", f"{year}-12-31", APP_VARIABLES)
    #mean over the 50 points for every hour
    hourly = pd.concat(frames)
    means = hourly.groupby("time").mean()
    return means.asfreq("h")


#the page calls this
#the weather of an area is one document in mongodb
#it is only downloaded when the document is missing
def area_weather(collection, region, year):
    name = f"{region}_{year}"
    document = collection.find_one({"_id": name})
    if document is None:
        series = download_area(region, year)
        document = {"_id": name, "region": region, "year": year, "n_points": 50}
        document["time"] = list(series.index.to_pydatetime())
        for variable in APP_VARIABLES:
            document[variable] = series[variable].tolist()
        collection.replace_one({"_id": name}, document, upsert=True)

    hours = pd.DatetimeIndex(document["time"], name="time")
    values = {variable: document[variable] for variable in APP_VARIABLES}
    return pd.DataFrame(values, index=hours)
