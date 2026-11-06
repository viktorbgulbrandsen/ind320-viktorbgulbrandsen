import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.fft import dct, idct
from scipy.signal import stft
from scipy.stats import median_abs_deviation
from sklearn.neighbors import LocalOutlierFactor
from statsmodels.tsa.seasonal import STL

YEAR = pd.Timedelta(days=365.25)


#rows in one year
#8766 for hourly weather and 52 for the weekly reservoir data
def per_year(series):
    step = series.index[1] - series.index[0]
    return YEAR / step


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


#one season is one year
def stl_plot(series, seasonal=13, trend=105, robust=False):
    period = round(per_year(series))
    stl = STL(series, period=period, seasonal=seasonal, trend=trend, robust=robust)
    fit = stl.fit()

    names = ["Observed", "Trend", "Seasonal", "Residual"]
    parts = [fit.observed, fit.trend, fit.seasonal, fit.resid]
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.06, subplot_titles=names)
    for row in range(4):
        fig.add_scatter(x=series.index, y=parts[row], line_color="steelblue", row=row + 1, col=1)
    fig.update_xaxes(title_text="Date", row=4, col=1)
    title = f"{series.name}, STL (seasonal {seasonal}, trend {trend})"
    fig.update_layout(title=title, height=800, showlegend=False)
    return fig


def spectrogram_plot(series, window_length=104, overlap=78):
    values = series.to_numpy(dtype=float)

    #fs is rows per year so the frequencies come out in cycles per year
    #detrend takes away the mean of each window
    #no boundary and no padding so every window lies fully inside the data
    fs = per_year(series)
    frequency, years, z = stft(values, fs=fs, nperseg=window_length, noverlap=overlap,
                               detrend="constant", boundary=None, padded=False)
    #the windows come back as years since the start
    centres = series.index[0] + pd.to_timedelta(years * 365.25, unit="D")

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.35, 0.65])
    fig.add_scatter(x=series.index, y=values, line_color="steelblue", row=1, col=1)
    #the colour bar is kept beside the heatmap
    colorbar = dict(title="Amplitude", len=0.65, y=0, yanchor="bottom")
    fig.add_heatmap(x=centres, y=frequency, z=np.abs(z), colorscale="Viridis", colorbar=colorbar, row=2, col=1)
    fig.update_yaxes(title_text=series.name, row=1, col=1)
    #above 6 cycles per year the reservoirs show nothing
    fig.update_yaxes(title_text="Frequency (cycles per year)", range=[0, 6], row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    title = f"{series.name}, spectrogram (window {window_length}, overlap {overlap})"
    fig.update_layout(title=title, height=650, showlegend=False)
    return fig
