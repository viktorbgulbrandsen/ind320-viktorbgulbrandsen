from functools import lru_cache
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import requests
import shapely

DATA = Path(__file__).resolve().parents[1] / "data"
SERVER = "https://kart.nve.no/enterprise/rest/services"

#the path of each layer on nve's map server
#and the field that names its shapes
LAYERS = {
    "budomraade": ("Nettomraader/MapServer/0", "budomr"),
    "nve_region": ("Mapservices/Administrasjon2/MapServer/0", "REGION"),
    "norge_n5000": ("Mapservices/Administrasjon2/MapServer/11", "OBJTYPE"),
}

#which shapes each area of magasinstatistikk is made of
#east is rø and rs together
#north is split into rm and rn
AREAS = {
    "NO": ("budomraade", ["NO 1", "NO 2", "NO 3", "NO 4", "NO 5"]),
    "NO1": ("budomraade", ["NO 1"]),
    "NO2": ("budomraade", ["NO 2"]),
    "NO3": ("budomraade", ["NO 3"]),
    "NO4": ("budomraade", ["NO 4"]),
    "NO5": ("budomraade", ["NO 5"]),
    "VASS1": ("nve_region", ["RØ", "RS"]),
    "VASS2": ("nve_region", ["RV"]),
    "VASS3": ("nve_region", ["RM"]),
    "VASS4": ("nve_region", ["RN"]),
}


#fetched from nve once and then kept as a shapefile
def read_layer(layer):
    file = DATA / "shapefiles" / layer / f"{layer}.shp"
    if not file.exists():
        path, field = LAYERS[layer]
        params = {"where": "1=1", "outFields": field, "returnGeometry": "true", "outSR": 25833, "f": "geojson"}
        response = requests.get(f"{SERVER}/{path}/query", params=params)
        response.raise_for_status()
        shapes = gpd.read_file(response.text)
        shapes = shapes.set_crs(25833, allow_override=True)
        file.parent.mkdir(parents=True, exist_ok=True)
        shapes[[field, "geometry"]].to_file(file, encoding="utf-8")
    return gpd.read_file(file)


#all land cover except the sea as one shape
#putting it together is slow so it is cached
@lru_cache
def land():
    cover = read_layer("norge_n5000")
    on_land = cover[cover["OBJTYPE"] != "Havflate"]
    return on_land.union_all()


#the area is cut to land so no point ends up in the sea
@lru_cache
def region_shape(region):
    layer, names = AREAS[region]
    shapes = read_layer(layer)
    field = LAYERS[layer][1]
    parts = shapes[shapes[field].isin(names)]
    together = parts.union_all()
    shape = together.intersection(land())
    shape = shapely.make_valid(shape)
    #the cut leaves stray lines and points along the borders
    polygons = [part for part in shapely.get_parts(shape) if part.geom_type == "Polygon"]
    shape = shapely.union_all(polygons)
    #the files are in utm and the points are wanted in lon and lat
    utm = gpd.GeoSeries([shape], crs=25833)
    lonlat = utm.to_crs(4326)
    return lonlat.iloc[0]


#the same seed gives the same points
def draw_points(region, n, seed):
    shape = region_shape(region)
    #the box to draw in is taken in an equal area projection
    #drawing straight in lon and lat would put the points too close in the north
    lonlat = gpd.GeoSeries([shape], crs=4326)
    equal_area = lonlat.to_crs(3035)
    xmin, ymin, xmax, ymax = equal_area.iloc[0].bounds
    rng = np.random.default_rng(seed)

    #keep what lands inside the area until there are n points
    kept = []
    found = 0
    while found < n:
        x = rng.uniform(xmin, xmax, 4 * n)
        y = rng.uniform(ymin, ymax, 4 * n)
        points = gpd.GeoSeries(gpd.points_from_xy(x, y), crs=3035)
        points = points.to_crs(4326)
        lon = points.x.to_numpy()
        lat = points.y.to_numpy()
        inside = shapely.contains_xy(shape, lon, lat)
        kept.append(pd.DataFrame({"lon": lon[inside], "lat": lat[inside]}))
        found += inside.sum()
    points = pd.concat(kept)
    points = points.head(n)
    return points.reset_index(drop=True)


#drawn once and kept as csv
#the weather files are named after these points so they must not change
def sample_points(region):
    file = DATA / f"points_{region}.csv"
    if not file.exists():
        points = draw_points(region, 1000, 320)
        points.to_csv(file, index=False)
    return pd.read_csv(file)
