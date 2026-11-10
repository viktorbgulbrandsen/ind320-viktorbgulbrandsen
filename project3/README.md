# Part 3, data quality

For the third part, weather is added to the reservoir data. I take the shapes of the ten areas of Magasinstatistikk from NVE's map server and draw 1000 random points inside each. For NO3 the hourly weather of 2024 is downloaded for all 1000 points from the open-meteo API. Then I look at the quality of the data: outliers in the precipitation by SPC limits, anomalies in the temperature by LOF, and the fill level of the reservoirs through STL and a spectrogram.

## Notebook

The notebook is 'part3.ipynb'. It starts with the open-meteo API, then the areas and the points, the download for NO3 and the four analyses. The log and the AI log are at the end. To run it you need geopandas from the dev group. The downloaded weather is kept in 'data/', which is not in the repository. The download function fetches what is missing.

## Pages

- **Fill level decomposition**: choose an area and get the STL split of its fill level in one tab and the spectrogram in the other. Sliders for the smoothers and the window.
- **Weather outliers**: hourly precipitation and temperature of 2024 for the chosen area, as the mean over 50 random points. One tab marks outliers in the precipitation, the other marks anomalies in the temperature. The weather is read from MongoDB, and downloaded from open-meteo the first time an area is asked for.

The **Plot** page from part 2 got an "All columns" choice. The menu at the root now holds the pages of part 2 and part 3 in one list.

## Structure

```
views/             the two new pages
utils/
  regions.py       the areas as shapes, and 1000 random points in each
  weather.py       the open-meteo download, for the notebook and for the app
  quality.py       SPC, LOF, STL and the spectrogram
data/
  points_50.json   the 50 points per area that the app downloads for
part3.ipynb
requirements.txt   the packages the app needs
```
