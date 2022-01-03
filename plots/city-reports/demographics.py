# Code written by Aaron Xie and Abhi Uppal, modified for script format by Abhi Uppal

import asyncio
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

from lowe.locations.lookup import name2fips
from lowe.acs.ACSClient import ACSClient

# Primary and secondary colors
pri_color = "#961a30"
sec_color = "#e7c8ae"


# ------------------------------
# Plot Generation
# ------------------------------


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
        title_font_family="Glacial Indifference",
        title_font_color="black",
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
    client = ACSClient()
    await client.initialize()
    try:
        test = await households_with_internet(client=client)
    finally:
        await client.close()
    test.show()
    return test


if __name__ == "__main__":
    asyncio.run(main())
