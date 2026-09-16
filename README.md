# IND320 dashboard

Project work for IND320 Data to Decision at NMBU. 

For the first part, we make a Streamlit app for Norwegian reservior filling data.

## Setup 
The project uses [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

This installs both the app packages and the Jupyter for the notebook. Note that 'requirements.txt' holds only the packages for the Streamlit app, while the Jupyter is synced from the 'uv.lock'. 

## Run the app

```bash
uv run streamlit run streamlit_app.py
```