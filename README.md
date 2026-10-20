# IND320 dashboard

Project work for IND320 Data to Decision at NMBU.

The work comes in four parts that build on each other. Each part has its own folder, so it is clear what belongs to which hand-in. A folder is not changed after its part is handed in.

- 'project1/': part 1, a Streamlit app for Norwegian reservoir filling data, read from a CSV.
- 'project2/': part 2, the same data from the NVE API, cross-border power flows from ENTSO-E through Cassandra, Spark and MongoDB, and the app on top of that.

Each folder has its own README.

## Setup
The project uses [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

This installs the app packages and Jupyter for the notebooks. Spark and the Cassandra driver are in the dev group, they are only needed for the part 2 notebook. Python 3.12, since Spark does not run on 3.14.

## Run the app

```bash
uv run streamlit run project2/streamlit_app.py
```

The live app at streamlit.app runs the same file. Each 'projectN/requirements.txt' holds only the packages the app itself needs.
