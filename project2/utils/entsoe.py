import os
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
TOKEN = os.environ["ENTSOE_API_KEY"]

URL = "https://web-api.tp.entsoe.eu/api"
NS = {"ns": "urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:0"}
PERIOD_TAG = "{urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:0}Period"


def fetch_flows(out_area, in_area, period_start, period_end):
    params = {
        "securityToken": TOKEN,
        "documentType": "A11",
        "in_Domain": in_area,
        "out_Domain": out_area,
        "periodStart": period_start,
        "periodEnd": period_end,
    }
    response = requests.get(URL, params=params)
    response.raise_for_status()
    root = ET.fromstring(response.text)

    frames = []
    for period in root.iter(PERIOD_TAG):
        start = pd.Timestamp(period.find("ns:timeInterval/ns:start", NS).text)
        end = pd.Timestamp(period.find("ns:timeInterval/ns:end", NS).text)
        step = pd.Timedelta(period.find("ns:resolution", NS).text)
        rows = []
        for point in period.findall("ns:Point", NS):
            position = int(point.find("ns:position", NS).text)
            quantity = float(point.find("ns:quantity", NS).text)
            rows.append({"position": position, "quantity": quantity})
        points = pd.DataFrame(rows).set_index("position")
        n = int((end - start) / step)
        points = points.reindex(range(1, n + 1))
        points["quantity"] = points["quantity"].ffill()
        points["time"] = start + (points.index - 1) * step
        frames.append(points.set_index("time"))

    flows = pd.concat(frames)
    flows["out_area"] = out_area
    flows["in_area"] = in_area
    return flows
