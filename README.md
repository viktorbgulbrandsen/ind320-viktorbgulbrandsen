# IND320 dashboard

Project work for IND320 Data to Decision at NMBU.

The work comes in four parts that build on each other. Each part has its own folder, so it is clear what belongs to which hand-in. The app is one app, and every part adds pages to it.

- 'project1/': part 1, a Streamlit app for Norwegian reservoir filling data, read from a CSV.
- 'project2/': part 2, the same data from the NVE API, cross-border power flows from ENTSO-E through Cassandra, Spark and MongoDB, and the app on top of that.
- 'project3/': part 3, weather from the open-meteo API for the reservoir areas, and four looks at data quality: outliers by SPC, anomalies by LOF, STL and a spectrogram.

Each folder has its own README.

## Setup
The project uses [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

This installs the app packages and Jupyter for the notebooks. Spark, the Cassandra driver and geopandas are in the dev group, they are only needed for the notebooks. Python 3.12, since Spark does not run on 3.14.

## Run the app

```bash
uv run streamlit run streamlit_app.py
```

The live app at streamlit.app runs the same 'streamlit_app.py' at the root. It collects the pages from 'project2/views/' and 'project3/views/' in one menu. The link has to stay the same through all four parts, and streamlit.app only looks for the file at the root. Each 'projectN/requirements.txt' holds only the packages the app itself needs.
