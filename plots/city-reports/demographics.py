# Code written by Aaron Xie and Abhi Uppal, modified for script format by Abhi Uppal

import asyncio
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

from lowe.locations.lookup import name2fips
from lowe.acs.ACSClient import ACSClient
from typing import Union

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources


# Primary and secondary colors
pri_color = "#961a30"
sec_color = "#e7c8ae"
ter_color = "#e6aeb7"

# ------------------------------
# Helper Functions
# ------------------------------


def _load_dof_data() -> pd.DataFrame:
    """Helper function to load in the population data"""
    with pkg_resources.open_text("lowe.dof.clean-data", "city.csv") as f:
        pop_data = pd.read_csv(f, index_col="Year")
    return pop_data


def _growth_rate(initial, final):
    """Calculates the growth rate between the initial and final values.
    NOTE: This does NOT produce a percentage"""
    return (final - initial) / initial


# ------------------------------
# Plot Generation
# ------------------------------

# Figure 1: City Population in Coachella Valley -- APPROVED


def city_population_cv_present(
    year: Union[int, str] = "2021",
    target_city: str = "Coachella",
    save: bool = False,
    save_path: str = None,
) -> go.Figure:
    # Load in data and filter for the correct year (casted to int)
    df = _load_dof_data()
    year = int(year) if isinstance(year, str) else year

    # Get city populations and store them in plot_df
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
    pops = []
    for city in cities:
        city_pop = df.loc[year, city]
        pops.append(city_pop)
    plot_df = pd.DataFrame({"City": cities, "Population": pops})
    plot_df = plot_df.sort_values(by="Population", ascending=False)

    # Plot!

    # Highlight the target city

    colors = [pri_color] * 9
    idx = list(plot_df.City).index(target_city.title())
    colors[idx] = sec_color

    fig = go.Figure()

    # Add the bar and mess with the formatting

    fig.add_trace(
        go.Bar(
            x=plot_df["City"],
            y=plot_df["Population"],
            text=plot_df["Population"].apply(lambda x: "{:,.0f}".format(x)),
            marker_color=colors,
        )
    )

    fig.update_layout(
        font_family="Glacial Indifference",
        font_color="black",
        yaxis_title="Population",
        legend_title_font_color="black",
        template="plotly_white",
        xaxis_title="City",
    )

    return fig


# Fig 2: City Population, CV, 1990-Present -- APPROVED


def city_population_cv_time_series(
    save: bool = False,
    save_path: str = None,
) -> go.Figure:
    # Load the data
    df = _load_dof_data()
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
    df = df[cities]
    plot_df = df.melt(
        ignore_index=False, value_vars=cities, var_name="City", value_name="Population"
    )

    print(plot_df)

    # Plot!

    fig = px.line(plot_df, x=plot_df.index, y="Population", color="City")

    fig.update_layout(
        font_family="Glacial Indifference",
        font_color="black",
        yaxis_title="Population",
        legend_title_font_color="black",
        template="plotly_white",
        xaxis_title="Year",
    )

    return fig


# Fig 3: Population Growth Rates, City, Rest of CV -- WIP


def pop_growth_rates(
    target_city: str = "Coachella", save: bool = False, save_path: str = None
) -> go.Figure:
    df = _load_dof_data()
    fig = go.Figure()
    return fig


# Fig 4: Population Growth Rates, 1999-2007, 2008-Present -- WIP
# NOTE: Needs to be checked by hand


def pop_growth_rates_year_groups(
    year: Union[int, str] = "2021", save: bool = False, save_path: str = None
) -> go.Figure:
    df = _load_dof_data()
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
    plot_df = df[cities]

    year = int(plot_df.index.max()) if year is None else int(year)

    group1 = [1997, 2007]
    initial_1 = plot_df.loc[group1[0], :]
    final_1 = plot_df.loc[group1[1], :]
    growth_rates_1 = _growth_rate(initial=initial_1, final=final_1)

    group2 = [2008, year]
    initial_2 = plot_df.loc[group2[0], :]
    final_2 = plot_df.loc[group2[1], :]
    growth_rates_2 = _growth_rate(initial=initial_2, final=final_2)

    # Plot!

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=plot_df.columns,
            y=growth_rates_1,
            text=np.array([*map(lambda x: "{:,.1f}%".format(x * 100), growth_rates_1)]),
            marker_color=pri_color,
            name=f"{group1[0]}-{group1[1]}",
        )
    )

    fig.add_trace(
        go.Bar(
            x=plot_df.columns,
            y=growth_rates_2,
            text=np.array([*map(lambda x: "{:,.1f}%".format(x * 100), growth_rates_2)]),
            marker_color=ter_color,
            name=f"{group2[0]}-{group2[1]}",
        )
    )

    fig.update_layout(
        font_family="Glacial Indifference",
        font_color="black",
        yaxis_title="Population Growth Rate",
        legend_title_font_color="black",
        template="plotly_white",
        xaxis_title="City",
    )
    return fig


# Fig 6: Race Group Distribution -- APPROVED


async def race_group_distribution(
    client: ACSClient,
    cities: list = ["desert hot springs, ca"],
    year: str = "2019",
    save: bool = False,
    save_path: str = None,
):
    """
    DO NOT PASS CITIES PARAM (is a list of them); if one city just pass as list of 1
    Parameters
    ----------
    city: name of the city eg.
    target
    save: bool
    True or False, whether or not you want to save
    save_path: str
    Path to save the file to
    """
    cols = {
        # old col name: new name
        "ACS DEMOGRAPHIC AND HOUSING ESTIMATES Percent RACE Total population One race White": "White alone",
        "ACS DEMOGRAPHIC AND HOUSING ESTIMATES Percent HISPANIC OR LATINO AND RACE Total population Not Hispanic or Latino White alone": "White Alone, not Hispanic or Latino",
        "ACS DEMOGRAPHIC AND HOUSING ESTIMATES Percent HISPANIC OR LATINO AND RACE Total population Hispanic or Latino (of any race)": "Hispanic or Latino",
        "ACS DEMOGRAPHIC AND HOUSING ESTIMATES Percent RACE Total population One race Black or African American": "Black or African American alone",
        "ACS DEMOGRAPHIC AND HOUSING ESTIMATES Percent HISPANIC OR LATINO AND RACE Total population Not Hispanic or Latino American Indian and Alaska Native alone": "American Indian and Alaska Native alone",
        "ACS DEMOGRAPHIC AND HOUSING ESTIMATES Percent RACE Total population One race Asian": "Asian alone",
        "ACS DEMOGRAPHIC AND HOUSING ESTIMATES Percent RACE Total population One race Native Hawaiian and Other Pacific Islander": "Native Hawaiian and Other Pacific Islander alone",
        "ACS DEMOGRAPHIC AND HOUSING ESTIMATES Percent RACE Total population Two or more races": "Two or more races",
    }

    loc_dicts = [{"city": city} for city in cities]
    loc_fips = [*map(name2fips, loc_dicts)]

    resp = await client.get_acs(
        vars=["DP05"], start_year=year, end_year=year, estimate="5", location=loc_fips
    )

    col_sub = [*list(cols.keys()), "state", "city"]
    resp = resp[col_sub]
    resp = resp.rename(columns=cols)

    # Following is unique to each section

    categ = resp.columns[0:8]
    value = resp.iloc[0][0:8].astype(str).astype(float)

    plot_df = pd.DataFrame({"Race": categ, "Percentage": value})
    plot_df = plot_df.sort_values(by="Percentage", ascending=False)

    fig = px.bar(
        plot_df,
        x="Race",
        y="Percentage",
        text=plot_df["Percentage"].apply(lambda x: "{0:,.1f}%".format(x)),
    )
    fig.update_xaxes(type="category")

    fig.update_layout(
        font_family="Glacial Indifference",
        font_color="black",
        yaxis_title="Percent of Population",
        legend_title_font_color="black",
        template="simple_white",
    )

    fig.update_xaxes(tickangle=20)

    fig.update_traces(marker_color=pri_color)

    if save:
        fig.write_image(save_path, format="png")
    return fig


# Fig 7: Households With Broadband Internet Access -- APPROVED


async def households_with_internet(
    client: ACSClient,
    cities: list = [
        "cathedral city, ca",
        "coachella, ca",
        "desert hot springs, ca",
        "indian wells, ca",
        "indio, ca",
        "la quinta, ca",
        "palm desert, ca",
        "palm springs, ca",
        "rancho mirage, ca",
    ],
    year: str = "2019",
    save: bool = False,
    save_path: str = None,
):
    """
    DO NOT PASS CITIES PARAM (is a list of them); if one city just pass as list of 1
    Parameters
    ----------
    city: name of the city eg.
    target
    save: bool
    True or False, whether or not you want to save
    save_path: str
    Path to save the file to
    """
    target_cols = "TYPES OF COMPUTERS AND INTERNET SUBSCRIPTIONS Estimate Percent Total households TYPE OF INTERNET SUBSCRIPTIONS With an Internet subscription: Broadband of any type"
    new_col_name = "Percent of Total Households with Broadband"

    loc_dicts = [{"city": city} for city in cities]
    loc_fips = [*map(name2fips, loc_dicts)]

    resp = await client.get_acs(
        vars=["S2801"], start_year=year, end_year=year, estimate="5", location=loc_fips
    )

    col_sub = [target_cols, "state", "city"]
    resp = resp[col_sub]
    resp = resp.rename(columns={target_cols: new_col_name})

    # Following is unique to each section

    categ = resp["city"]
    value = resp["Percent of Total Households with Broadband"].astype(str).astype(float)

    plot_df = pd.DataFrame({"Type": categ, "Value": value})
    plot_df["Type"] = plot_df["Type"].str.title()
    plot_df = plot_df.sort_values(by="Value", ascending=False)

    fig = px.bar(
        plot_df,
        x="Type",
        y="Value",
        text=plot_df["Value"].apply(lambda x: "{0:,.1f}%".format(x)),
    )
    fig.update_xaxes(type="category")

    fig.update_layout(
        font_family="Glacial Indifference",
        font_color="black",
        title_font_family="Glacial Indifference",
        title_font_color="black",
        legend_title_font_color="black",
        template="simple_white",
        xaxis_title="City",
        yaxis_title="Percent of Households",
    )

    fig.update_traces(marker_color=pri_color)

    if save:
        fig.write_image(save_path, format="png")
    return fig


# ------------------------------
# Testing Code
# ------------------------------


async def main():
    test = pop_growth_rates_year_groups(year=2020)
    test.show()


if __name__ == "__main__":
    asyncio.run(main())
