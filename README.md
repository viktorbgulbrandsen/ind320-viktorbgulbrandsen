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


## Pages on the app

- **Home**: index for the app, information
- **Data table**: showing the reservoir data in table format
- **Plot**: showing the reservoir data by plot
- **Latest week**: showing last week of the data

## Data


## Data

'data/reservoirs.csv' is from the course repository [khliland/IND320](https://github.com/khliland/IND320). It has weekly reservoir data from 1995 to 2026 for 9 areas. The table and plot pages use the national total.

## Structure

```
streamlit_app.py   sidebar menu
reservoirs.py      cached CSV loader, English column names
pages/             one file per page
notebooks/         part1.ipynb, the data work and the log
data/              reservoirs.csv
```
