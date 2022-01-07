# Code written by Abhi Uppal

import asyncio
import pandas as pd
import plotly.graph_objects as go
import requests
import time


from functools import wraps, lru_cache
from lowe.FRED.FREDClient import FREDClient

# Primary and secondary colors
pri_color = "#961a30"
sec_color = "#e7c8ae"
ter_color = "#e6aeb7"

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

# Figure 21: Real and Nominal Taxable Retail Sales Per Capita in City, 2010-Present -- WIP


async def real_nominal_sales_pc_time_series(
    city: str = "Cathedral City", data_path: str = None
):
    # Load in the data and filter for the annual data for the city of interest
    df = _load_data(data_path)
    df = df[df["City"].str.lower().str.contains(city.lower())]
    df = df[df["Quarter"].str.contains("A")]

    df = df.sort_values(by="CalendarYear", ascending=True)

    # Get CPI

    client = FREDClient()
    await client.initialize()

    try:
        res = await client.get_fred(
            vars=["CPIAUCSL"],
            startDate="2010-01-01",
            endDate="2021-01-01",
            frequency="a",
            export=False,
            file_type=".xls",
            debug=False,
        )
    finally:
        await client.close()

    print(res)
    # Plot!

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df["CalendarYear"],
            y=df["PerCapita"],
            marker_color=pri_color,
            name="Nominal Retail Sales Per Capita",
        )
    )

    return df


def taxable_sales_per_capita_quarters_cv(data_path: str = None):
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


async def main():
    test = await real_nominal_sales_pc_time_series(
        city="Desert Hot Springs", data_path="data/taxable_sales.csv"
    )
    print(test)


if __name__ == "__main__":
    asyncio.run(main())
