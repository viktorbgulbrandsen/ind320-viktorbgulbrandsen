# Part 1, dashboard basics

Handed in 29 September 2026. Not changed after that.

A Streamlit app for Norwegian reservoir filling data, read from 'data/reservoirs.csv' (from the course repository [khliland/IND320](https://github.com/khliland/IND320)). Weekly data from 1995 to 2026 for 9 areas. The table and plot pages use the national total.

## Pages

- **Home**: index for the app, information
- **Data table**: the reservoir data in table format
- **Plot**: the reservoir data by plot
- **Latest week**: the last week of the data, per area

## Structure

```
streamlit_app.py   sidebar menu
reservoirs.py      cached CSV loader, English column names
pages/             one file per page
part1.ipynb        the data work and the log
data/              reservoirs.csv
```

Run from this folder with 'uv run streamlit run streamlit_app.py'.
