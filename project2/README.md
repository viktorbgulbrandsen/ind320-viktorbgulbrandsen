# Part 2, data sources

For the second part, the reservoir data is read from the NVE API instead of the CSV. I also get two years of power flows between Norway and the neighbouring countries from the ENTSO-E API. These are written to Cassandra with Spark, read back with Spark and put into MongoDB. The app reads the flows from there.

## Notebook

The notebook is 'part2.ipynb'. It starts with the NVE API, then the ENTSO-E API, then Cassandra and Spark, the plots and MongoDB. The log and the AI log are at the end. To run it you need Cassandra in Docker, Java 17 for Spark and a MongoDB Atlas cluster.

## Pages

- **Home**
- **Data table**: choose EL, NO or VASS and get one row per area with a small line chart per column. The slider chooses the months.
- **Plot**: one column, one line per area.
- **Cross-border flows**: choose a connection and a year and get a pie chart of the flow in and out of Norway. Choose months and get a line plot per direction. This page reads from MongoDB.
- **Latest week**: fill level per area in the last week.

## Structure

```
streamlit_app.py   sidebar menu
views/             one file per page
utils/
  nve.py           the reservoir data and the area list
  entsoe.py        the ENTSO-E flows, from XML to a table
  mongo.py         the MongoDB client and the queries
part2.ipynb
requirements.txt   the packages the app needs
```
