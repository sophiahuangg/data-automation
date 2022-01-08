# Code written by Abhi Uppal

import os
import pandas as pd
import plotly.graph_objects as go
import requests
import time

from datetime import datetime
from demographics import _load_dof_data  # Get the helper from the demographics file
from dotenv import load_dotenv
from functools import wraps, lru_cache

# Primary and secondary colors
pri_color = "#961a30"
sec_color = "#e7c8ae"
ter_color = "#e6aeb7"
qua_color = "#bf5e5e"
pen_color = "#9c4d48"

# ------------------------------
# Helper Functions
# ------------------------------


def timer(f):
    """Decorator that times the amount of time it takes a function to
    complete and prints it to standard output"""

    @wraps(f)
    def wrapper(*args, **kwargs):
        t0 = time.time()
        res = f(*args, **kwargs)
        tf = time.time()
        print(f"Time for function {f.__name__} to run: {tf - t0:.1f} seconds.")
        return res

    return wrapper


@timer
@lru_cache()
def _get_data(save_path: str = None):
    """Gets Taxable Sales data and caches it for future function calls
    Returns a pandas DataFrame"""
    # Get the data
    uri = "https://www.cdtfa.ca.gov/dataportal/api/odata/Taxable_Sales_by_City"
    r = requests.get(uri)
    js = r.json()

    # Put the data into a pd DataFrame and clean it
    res = pd.json_normalize(js, record_path="value")
    res = res[~res["PerCapita"].isna()]
    res = res.drop(columns="DisclosureFlag")
    res = res.reset_index(drop=True)

    if save_path is not None:
        res.to_csv(save_path, index=False)

    return res


def _load_data(data_path: str = None):
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        df = _get_data()
    return df


# ------------------------------
# Plot Generation
# ------------------------------

# Figure 21: Real and Nominal Taxable Retail Sales Per Capita in City, 2010-Present -- APPROVED


def real_nominal_sales_pc_time_series(
    city: str = "Cathedral City", data_path: str = None
):
    """real_nominal_sales_pc_time_series [summary]
    NOTE: Yearly CPI numbers are released around January 12th of the following year.
    So, the plot should be re-generated after then. Otherwise, the last year's CPI number will be inaccurate.

    Parameters
    ----------
    city : str, optional
        [description], by default "Cathedral City"
    data_path : str, optional
        [description], by default None

    Returns
    -------
    [type]
        [description]
    """
    # Load in the data and filter for just the quarterly data for the city of interest
    # The quarterly data will be aggregated with a groupby
    df = _load_data(data_path)
    df = df[df["City"].str.lower().str.contains(city.lower())]
    df = df[~df["Quarter"].str.contains("A")]

    df = df.sort_values(by="CalendarYear", ascending=True)

    # Find out what quarter the last year goes up to -- a bit involved :)

    maxYear = df["CalendarYear"].max()
    maxYear_df = df[df["CalendarYear"] == maxYear]
    maxMonth = maxYear_df["QuarterMonthTo"].max()
    maxQuarter = maxMonth // 3

    last_year_descriptor = (
        f"{maxYear}" if maxQuarter == 4 else f"{maxYear} (Q{maxQuarter})"
    )

    # Aggregate the data and get the total taxable sales for each year

    df = df.groupby("CalendarYear").agg(
        {"RetailandFoodServicesTaxableTransactions": "sum"}
    )

    # Get CPI for inflation adjustment
    load_dotenv()
    date = datetime.today()
    yr = date.year
    apiKey = os.environ.get("API_KEY_FRED", None)
    assert (
        apiKey is not None
    ), "Please ensure API_KEY_FRED is specified in your .env file."

    base = "https://api.stlouisfed.org/fred/series/observations"

    params = {
        "series_id": "CPIAUCSL",
        "observation_start": "2010-01-01",
        "observation_end": f"{yr}-01-01",
        "frequency": "m",
        "api_key": apiKey,
        "file_type": "json",
    }

    r = requests.get(base, params).json()
    cpi_df = pd.json_normalize(r, record_path="observations")
    cpi_df["year"] = cpi_df["date"].apply(
        lambda x: datetime.strptime(x, "%Y-%m-%d").year
    )
    cpi_df["value"] = cpi_df["value"].astype(float)
    cpi_df = (
        cpi_df.groupby("year").agg({"value": "mean"}).rename(columns={"value": "CPI"})
    )

    # Get Population data

    pop = _load_dof_data(filter_cities=True)
    pop = pop[city.title()]

    # Join the datasets together

    plot_df = (
        df.merge(cpi_df, left_index=True, right_index=True)
        .merge(pop, left_index=True, right_index=True)
        .rename(
            columns={
                f"{city.title()}": "Population",
                "RetailandFoodServicesTaxableTransactions": "Retail Sales",
            }
        )
    )

    # Calculate the columns we need

    first_year_cpi = plot_df.loc[plot_df.index.min(), "CPI"]
    plot_df["adj factor"] = first_year_cpi / plot_df["CPI"]
    plot_df["Retail Adj"] = plot_df["Retail Sales"] * plot_df["adj factor"]

    plot_df["Per Capita"] = plot_df["Retail Sales"] / plot_df["Population"]
    plot_df["Per Capita Adj"] = plot_df["Retail Adj"] / plot_df["Population"]

    dateList = list(plot_df.index)
    dateList[-1] = last_year_descriptor
    dateList = [*map(str, dateList)]

    # Plot!
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=dateList,
            y=list(plot_df["Per Capita"]),
            name="Nominal Taxable Sales Per Capita",
            marker_color=pri_color,
            text=plot_df["Per Capita"].apply(lambda x: "{:,.0f}".format(x)),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=dateList,
            y=list(plot_df["Per Capita Adj"]),
            name=f"Real Taxable Sales Per Capita ({dateList[0]} Dollars)",
            marker_color=sec_color,
        )
    )

    fig.update_layout(
        font_family="Glacial Indifference",
        font_color="black",
        yaxis_title="Taxable Retail and Food Sales",
        legend_title_font_color="black",
        template="plotly_white",
        xaxis_title="Year",
        legend=dict(x=0.5, orientation="h", xanchor="center"),
    )

    return fig


# Figure 22: Taxable Sales Per Capita, Latest Year


def taxable_sales_per_capita_quarters_cv(data_path: str = None, *args, **kwargs):
    # Load in the data
    df = _load_data(data_path)

    cities = [
        "Coachella",
        "Cathedral City",
        "Desert Hot Springs",
        "Indian Wells",
        "Indio",
        "La Quinta",
        "Palm Desert",
        "Palm Springs",
        "Rancho Mirage",
    ]

    pattern = "|".join(cities)

    # Get the cities of interest and filter for the latest year and correct cities

    maxYear = df["CalendarYear"].astype(int).max()
    df = df[df["City"].str.contains(pattern)]
    df = df[~df["Quarter"].str.contains("A")]
    df = df[df["CalendarYear"].astype(int) == maxYear]

    numQuarters = df["QuarterMonthTo"].max() // 3
    sub_dfs = [df[df["Quarter"] == f"Q{q}"] for q in range(1, numQuarters + 1)]

    colors = [pri_color, qua_color, ter_color, pen_color]

    fig = go.Figure()

    for i, data in enumerate(sub_dfs):
        fig.add_trace(
            go.Bar(
                x=data["City"],
                y=data["PerCapita"],
                name=f"Quarter {i + 1}",
                text=data["PerCapita"].apply(lambda x: "{:,.0f}".format(x)),
                marker_color=colors[i],
            )
        )

    fig.update_layout(
        font_family="Glacial Indifference",
        font_color="black",
        yaxis_title="Taxable Retail and Food Sales",
        legend_title_font_color="black",
        template="plotly_white",
        xaxis_title="City",
        legend=dict(x=0.5, orientation="h", xanchor="center"),
    )

    return fig


def main():
    test = taxable_sales_per_capita_quarters_cv(data_path="data/taxable_sales.csv")
    test.show()


if __name__ == "__main__":
    main()
