import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


#uri from .env, or from the streamlit secrets when running online
def get_client():
    uri = os.environ.get("MONGO_URI")
    if uri is None:
        import streamlit as st

        uri = st.secrets["mongo"]["uri"]
    return MongoClient(uri)


#names of the connections in the collection
def list_connections(client):
    collection = client["ind320"]["flows"]
    return sorted(collection.distinct("connection"))


#all flows of one connection, both directions
def load_flows(client, connection):
    collection = client["ind320"]["flows"]
    rows = collection.find({"connection": connection}, {"_id": 0})
    return pd.DataFrame(list(rows), columns=["connection", "direction", "time", "quantity"])
