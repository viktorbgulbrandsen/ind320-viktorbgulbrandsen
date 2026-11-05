import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.fft import dct, idct
from scipy.stats import median_abs_deviation
from sklearn.neighbors import LocalOutlierFactor

YEAR = pd.Timedelta(days=365.25)


#the plot is labelled with the name of the series
#cutoff is in cycles per year
def spc_outliers(series, cutoff=12, n_std=3):
    values = series.to_numpy(dtype=float)

    #dct type 1 as in the book
    #coefficient k holds k/2 cosine cycles over the whole series
    years = (series.index[-1] - series.index[0]) / YEAR
    frequency = np.arange(len(values)) / (2 * years)

    #zero the slow coefficients and transform back
    #what is left is the satv
    coefficients = dct(values, type=1, norm="forward")
    coefficients[frequency < cutoff] = 0
    satv = idct(coefficients, type=1, norm="forward")

    #median and mad so the outliers themselves do not move the limits
    centre = np.median(satv)
    spread = median_abs_deviation(satv, scale="normal")
    low = centre - n_std * spread
    high = centre + n_std * spread
    flagged = (satv < low) | (satv > high)

    #the satv is not plotted
    #the limits are put back on top of the slow part that the filter removed
    slow = values - satv

    fig = go.Figure()
    fig.add_scatter(x=series.index, y=values, name=series.name)
    fig.add_scatter(x=series.index[flagged], y=values[flagged], name="Outliers", mode="markers", marker_color="red", marker_size=4)
    fig.add_scatter(x=series.index, y=slow + high, name="Upper SPC limit", line_color="black", line_dash="dash")
    fig.add_scatter(x=series.index, y=slow + low, name="Lower SPC limit", line_color="black", line_dash="dot")
    title = f"{series.name}, SPC limits ({n_std:g} SD, cut-off {cutoff:g} per year)"
    fig.update_layout(title=title, xaxis_title="Time", yaxis_title=series.name, margin_t=60)

    outliers = pd.DataFrame({"time": series.index[flagged], "value": values[flagged]})
    summary = {"n_outliers": len(outliers), "share": flagged.mean(), "limits": (low, high), "outliers": outliers}
    return fig, summary


#contamination is the share that gets marked
def lof_anomalies(series, contamination=0.01):
    values = series.to_numpy(dtype=float)

    #lof on the value alone would mostly find the coldest and warmest hours
    #with time as a second feature a value is compared with the hours around it
    #one hour counts as 0.01 so a day is about a quarter of a standard deviation
    z = (values - values.mean()) / values.std()
    hours = (series.index - series.index[0]) / pd.Timedelta(hours=1)
    features = np.column_stack([z, 0.01 * hours])

    #20 neighbours as in the book
    lof = LocalOutlierFactor(n_neighbors=20, contamination=contamination)
    flagged = lof.fit_predict(features) == -1
    scores = -lof.negative_outlier_factor_

    fig = go.Figure()
    fig.add_scatter(x=series.index, y=values, name=series.name)
    fig.add_scatter(x=series.index[flagged], y=values[flagged], name="LOF anomalies", mode="markers", marker_color="red")
    title = f"{series.name}, LOF anomalies ({contamination:.1%} marked)"
    fig.update_layout(title=title, xaxis_title="Time", yaxis_title=series.name, margin_t=60)

    anomalies = pd.DataFrame({"time": series.index[flagged], "value": values[flagged], "lof": scores[flagged]})
    summary = {"n_anomalies": len(anomalies), "share": flagged.mean(), "anomalies": anomalies}
    return fig, summary
