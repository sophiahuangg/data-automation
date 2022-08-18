# Code written by Aaron Xie and Abhi Uppal, modified for script format by Abhi Uppal

import asyncio
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go

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

# Fundamental colors
fund_pri = "#961a30"
fund_sec = "#c5485f"
fund_ter = "#e6aeb7"

# Accent Colors
acc_pri = "#965119"
acc_sec = "#c57a49"
acc_ter = "#e7c8ae"

# todo:
# fix target city
# check FIGURE OUT %

# ------------------------------
# Helper Functions
# ------------------------------


def _load_dof_data(filter_cities: bool = False) -> pd.DataFrame:
    """Helper function to load in the population data"""
    with pkg_resources.open_text("lowe.dof.clean-data", "city.csv") as f:
        pop_data = pd.read_csv(f, index_col="Year")
    if filter_cities:
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
        pop_data = pop_data[cities]
    return pop_data


def _growth_rate(initial, final):
    """Calculates the growth rate between the initial and final values.
    NOTE: This does NOT produce a percentage"""
    return (final - initial) / initial


def _axis_line_breaks_elem(elem: str, max_chars: int = 15):
    """Adds line breaks to axis values so they can be plotted horizontally"""
    splt = elem.split(" ")
    res = ""
    tmp = ""
    for word in splt:
        res += f"{word} "
        tmp += f"{word} "
        charcount = len(tmp.strip())
        if charcount >= max_chars:
            res += "<br>"
            tmp = ""
            charcount = 0

    return res.strip()


def _axis_line_breaks(elems: list, max_chars: int = 15):
    return [*map(lambda x: _axis_line_breaks_elem(x, max_chars), elems)]


# ------------------------------
# Plot Generation
# ------------------------------

# Figure 1: City Population in Coachella Valley -- APPROVED


def city_population_cv_present(
    year: Union[int, str] = "2021",
    target_city: str = "Coachella",
    save_path: str = None,
    img_height: int = 1080,
    img_width: int = 1920,
    scale: int = 2,
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
    colors[idx] = fund_ter

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
        font_size=18,
        yaxis_title="Population",
        legend_title_font_color="black",
        template="plotly_white",
    )

    fig.update_traces(width=0.5, textposition="outside")

    if save_path is not None:
        fig.write_image(
            save_path, height=img_height, width=img_width, scale=scale, format="png"
        )

    return fig


# Fig 2: City Population, CV, 1990-Present -- APPROVED


def city_population_cv_time_series(
    save_path: str = None, img_height: int = 1080, img_width: int = 1920, scale: int = 2
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

    # Plot!

    colors = [
        "#ff0000",
        "#ffa500",
        "#ffff00",
        "#008000",
        "#0000ff",
        "#4b0082",
        "#ee82ee",
        "#00FFFF",
        "#000000",
    ]

    fig = px.line(
        plot_df,
        x=plot_df.index,
        y="Population",
        color="City",
        color_discrete_sequence=colors,
    )

    fig.update_layout(
        font_family="Glacial Indifference",
        font_color="black",
        font_size=22,
        yaxis_title="Population",
        legend_title_font_color="black",
        template="plotly_white",
        xaxis_title="Year",
    )

    fig.update_traces(line=dict(width=3), textposition="bottom right")

    if save_path is not None:
        fig.write_image(
            save_path, height=img_height, width=img_width, scale=scale, format="png"
        )

    return fig


# Fig 3: Population Growth Rates, City, Rest of CV -- APPROVED


def pop_growth_rates(
    target_city: str = "Coachella",
    save_path: str = None,
    img_height: int = 1080,
    img_width: int = 1920,
    scale: int = 2,
) -> go.Figure:
    df = _load_dof_data(filter_cities=True)
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

    # In case we mess up the city capitalization
    target_city = target_city.title()

    # Get a column for CV excluding the target city
    colname_cv_excl = f"CV Excl. {target_city}"

    df[colname_cv_excl] = 0
    for city in cities:
        if city != target_city:
            df[colname_cv_excl] += df[city]

    # Calculate growth rates

    df["g_target"] = df[target_city].pct_change()
    df["g_rest_cv"] = df[colname_cv_excl].pct_change()

    df = df[["g_target", "g_rest_cv"]]

    # Plot!

    fig = go.Figure()

    # Bar plot for target city
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["g_target"],
            marker_color=pri_color,
            text=df["g_target"].apply(lambda x: "{:.1f}%".format(x * 100)),
            name=f"{target_city}",
        )
    )

    # Bar pot for rest of CV
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["g_rest_cv"],
            marker_color=ter_color,
            text=df["g_rest_cv"].apply(lambda x: "{:.1f}%".format(x * 100)),
            name="Rest of CV",
        )
    )

    fig.update_layout(
        font_family="Glacial Indifference",
        font_color="black",
        font_size=18,
        yaxis_title="Population Growth Rate",
        legend_title_font_color="black",
        template="plotly_white",
        legend=dict(x=0.5, orientation="h", xanchor="center"),
    )

    fig.update_traces(textposition="outside")

    if save_path is not None:
        fig.write_image(
            save_path, height=img_height, width=img_width, scale=scale, format="png"
        )

    return fig


# Fig 4: Population Growth Rates, 1999-2007, 2008-Present -- APPROVED


def pop_growth_rates_year_groups(
    year: Union[int, str] = None,
    save_path: str = None,
    img_height: int = 1080,
    img_width: int = 1920,
    scale: int = 2,
) -> go.Figure:
    plot_df = _load_dof_data(filter_cities=True)

    year = int(plot_df.index.max()) if year is None else int(year)

    group1 = [1999, 2007]
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
        font_size=18,
        yaxis_title="Population Growth Rate",
        legend_title_font_color="black",
        template="plotly_white",
    )

    fig.update_traces(textposition="outside")

    if save_path is not None:
        fig.write_image(
            save_path, height=img_height, width=img_width, scale=scale, format="png"
        )

    return fig


# Fig 5: Age Distribution Graph -- APPROVED


async def age_distribution(
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
    target_city: str = "desert hot springs ca",
    save_path: str = None,
    img_height: int = 1080,
    img_width: int = 1920,
    scale: int = 2,
) -> go.Figure:
    # Location City Dictionary and Fips code
    loc_dicts = [{"city": city} for city in cities]
    loc_fips = [*map(name2fips, loc_dicts)]
    county = [{"county": "06_065"}]

    resp = await client.get_acs(
        vars=["S0101"],
        start_year=year,
        end_year=year,
        location=loc_fips + county,
        estimate="5",
        debug=False,
    )

    cols_mask = resp.columns.str.contains(
        "AGE AND SEX Estimate Percent|AGE AND SEX Estimate Total Total|city|location_key"
    )
    resp = resp.loc[:, cols_mask]
    no_gender_mask = ~resp.columns.str.contains("male|female|Male|Female|MALE|FEMALE")
    resp = resp.loc[:, no_gender_mask]
    other_mask = ~resp.columns.str.contains(
        "SELECTED AGE CATEGORIES|SUMMARY INDICATORS|PERCENT ALLOCATED"
    )
    resp = resp.loc[:, other_mask]

    # Renaming the columns to remove long ACS title leaving the age range only
    resp = resp.rename(
        columns=lambda x: x.replace(
            "AGE AND SEX Estimate Percent Total population AGE ", ""
        )
    )
    resp = resp.rename(
        columns={"AGE AND SEX Estimate Total Total population": "Total population"}
    )

    # Consolidating the age groups
    resp["0-14 years perc"] = (
        resp["Under 5 years"].astype(float)
        + resp["5 to 9 years"].astype(float)
        + resp["10 to 14 years"].astype(float)
    )

    resp["15-24 years perc"] = resp["15 to 19 years"].astype(float) + resp[
        "20 to 24 years"
    ].astype(float)

    resp["25-34 years perc"] = resp["25 to 29 years"].astype(float) + resp[
        "30 to 34 years"
    ].astype(float)

    resp["35-44 years perc"] = resp["35 to 39 years"].astype(float) + resp[
        "40 to 44 years"
    ].astype(float)

    resp["45-64 years perc"] = (
        resp["45 to 49 years"].astype(float)
        + resp["50 to 54 years"].astype(float)
        + resp["55 to 59 years"].astype(float)
        + resp["60 to 64 years"].astype(float)
    )

    resp["65+ years perc"] = (
        resp["65 to 69 years"].astype(float)
        + resp["70 to 74 years"].astype(float)
        + resp["75 to 79 years"].astype(float)
        + resp["80 to 84 years"].astype(float)
        + resp["85 years and over"].astype(float)
    )

    perc_cols = [
        "0-14 years perc",
        "15-24 years perc",
        "25-34 years perc",
        "35-44 years perc",
        "45-64 years perc",
        "65+ years perc",
    ]

    raw_cols = [
        "0-14 years",
        "15-24 years",
        "25-34 years",
        "35-44 years",
        "45-64 years",
        "65+ years",
    ]

    for i, colname in enumerate(raw_cols):
        resp[colname] = (
            resp[perc_cols[i]].astype(float)
            * resp["Total population"].astype(float)
            * 0.01
        )

    cols = ["location_key"] + perc_cols + raw_cols + ["Total population"]

    resp = resp[cols]

    resp["Total population"] = resp["Total population"].astype(float)

    # Adding values of each city per section to get Coachella Valley values
    cv = resp.loc[resp["location_key"] != "riverside county ca"]

    cv = cv.groupby(["year"]).sum()

    for i, colname in enumerate(perc_cols):
        cv[perc_cols[i]] = cv[raw_cols[i]] / cv["Total population"]

    cv["location_key"] = "Coachella Valley"

    # Dataframe for Coachella Valley ONLY
    cv_df = cv[cols]

    # Dataframe for riverside county ONLY
    rc_df = resp[resp["location_key"] == "riverside county ca"]

    # Following is unique to each city

    city_df = resp[resp["location_key"] == target_city]

    # Riverside county and Coachella Valley values without the target city
    rcxcity = rc_df.drop(columns=["location_key"]).subtract(
        city_df.drop(columns=["location_key"])
    )
    cvxcity = cv_df.drop(columns=["location_key"]).subtract(
        city_df.drop(columns=["location_key"])
    )

    # Getting riverside county and coachella valley perc without the target city
    rcxcity_perc = [
        *map(
            lambda categ: rcxcity.iloc[0][categ] / rcxcity.iloc[0]["Total population"],
            raw_cols,
        )
    ]

    cvxcity_perc = [
        *map(
            lambda categ: cvxcity.iloc[0][categ] / cvxcity.iloc[0]["Total population"],
            raw_cols,
        )
    ]

    # Plot!
    city_name = target_city[0 : (len(target_city)) - 2].title()

    x_axis = [
        city_name,
        f"Riverside County Excluding {city_name}",
        f"Coachella Valley Excluding {city_name}",
    ]

    y1 = pd.Series(
        [
            city_df.iloc[0]["0-14 years perc"],
            cvxcity_perc[0] * 100,
            rcxcity_perc[0] * 100,
        ]
    )
    y2 = pd.Series(
        [
            city_df.iloc[0]["15-24 years perc"],
            cvxcity_perc[1] * 100,
            rcxcity_perc[1] * 100,
        ]
    )
    y3 = pd.Series(
        [
            city_df.iloc[0]["25-34 years perc"],
            cvxcity_perc[2] * 100,
            rcxcity_perc[2] * 100,
        ]
    )
    y4 = pd.Series(
        [
            city_df.iloc[0]["35-44 years perc"],
            cvxcity_perc[3] * 100,
            rcxcity_perc[3] * 100,
        ]
    )
    y5 = pd.Series(
        [
            city_df.iloc[0]["45-64 years perc"],
            cvxcity_perc[4] * 100,
            rcxcity_perc[4] * 100,
        ]
    )
    y6 = pd.Series(
        [
            city_df.iloc[0]["65+ years perc"],
            cvxcity_perc[5] * 100,
            rcxcity_perc[5] * 100,
        ]
    )

    fig = go.Figure(
        data=[
            go.Bar(
                name="0-14 Years",
                x=x_axis,
                y=y1,
                text=y1.apply(lambda x: "{0:1.1f}%".format(x)),
                textposition="outside",
                marker_color=pri_color,
            ),
            go.Bar(
                name="15-24 Years",
                x=x_axis,
                y=y2,
                text=y2.apply(lambda x: "{0:1.1f}%".format(x)),
                textposition="outside",
                marker_color=fund_sec,
            ),
            go.Bar(
                name="25-34 Years",
                x=x_axis,
                y=y3,
                text=y3.apply(lambda x: "{0:1.1f}%".format(x)),
                textposition="outside",
                marker_color=fund_ter,
            ),
            go.Bar(
                name="35-44 Years",
                x=x_axis,
                y=y4,
                text=y4.apply(lambda x: "{0:1.1f}%".format(x)),
                textposition="outside",
                marker_color=sec_color,
            ),
            go.Bar(
                name="45-64 Years",
                x=x_axis,
                y=y5,
                text=y5.apply(lambda x: "{0:1.1f}%".format(x)),
                textposition="outside",
                marker_color=acc_sec,
            ),
            go.Bar(
                name="65+ Years",
                x=x_axis,
                y=y6,
                text=y6.apply(lambda x: "{0:1.1f}%".format(x)),
                textposition="outside",
                marker_color=acc_pri,
            ),
        ]
    )

    fig.update_layout(
        barmode="group",
        template="plotly_white",
        font=dict(family="Glacial Indifference", size=18, color="Black"),
        xaxis_title="Region",
        yaxis_title="Percent of Total Population",
    )

    if save_path is not None:
        fig.write_image(
            save_path, height=img_height, width=img_width, scale=scale, format="png"
        )

    return fig


# Fig 6: Race Group Distribution -- APPROVED


async def race_group_distribution(
    client: ACSClient,
    cities: list = ["desert hot springs, ca"],
    year: str = "2019",
    save_path: str = None,
    img_height: int = 1080,
    img_width: int = 1920,
    scale: int = 2,
) -> go.Figure:
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

    categ = _axis_line_breaks(categ, 10)

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
        font_size=18,
        yaxis_title="Percent of Population",
        legend_title_font_color="black",
        template="simple_white",
        yaxis=dict(ticksuffix="%"),
    )

    fig.update_xaxes(tickangle=0)

    fig.update_traces(marker_color=pri_color, width=0.5, textposition="outside")

    if save_path is not None:
        fig.write_image(
            save_path, height=img_height, width=img_width, scale=scale, format="png"
        )

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
    target_city: str = "desert hot springs ca",
    save_path: str = None,
    img_height: int = 1080,
    img_width: int = 1920,
    scale: int = 2,
) -> go.Figure:
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

    # ISOLATING TARGET CITY
    city_list = plot_df["Type"].values.tolist()
    city_index = city_list.index(target_city.split(",")[0].title())
    colors = [
        pri_color,
    ] * len(cities)
    colors[city_index] = fund_ter

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
        font_size=18,
        title_font_family="Glacial Indifference",
        title_font_color="black",
        legend_title_font_color="black",
        template="simple_white",
        xaxis_title="City",
        yaxis_title="Percent of Households",
        yaxis=dict(ticksuffix="%"),
    )

    fig.update_traces(marker_color=colors, textposition="outside", width=0.5)

    if save_path is not None:
        fig.write_image(
            save_path, height=img_height, width=img_width, scale=scale, format="png"
        )

    return fig


# Table 1: Residence and Work Location -- WIP


async def residence_and_work_loc(
    client: ACSClient,
    cities: list = ["desert hot springs, ca"],
    year: str = "2019",
    save_path: str = None,
    img_height: int = 1080,
    img_width: int = 1920,
    scale: int = 2,
):
    """
    Parameters
    ----------
    client: intialized ACS Client from lowe.acs.ACSClient
    city: name of the city eg.
    target
    year: str
        Year to get the data for
    save: bool
    True or False, whether or not you want to save
    save_path: str
    Path to save the file to
    """
    cols = {
        # old col name: new name
        "COMMUTING CHARACTERISTICS BY SEX Estimate Total PERCENT ALLOCATED Place of work": "% Allocated Place of Work",
        "COMMUTING CHARACTERISTICS BY SEX Estimate Total Workers 16 years and over PLACE OF WORK Not living in 12 selected states": "Count, live outside state",
        "COMMUTING CHARACTERISTICS BY SEX Estimate Total Workers 16 years and over PLACE OF WORK Worked in state of residence Worked outside county of residence": "Count, outside of county",
        "COMMUTING CHARACTERISTICS BY SEX Estimate Total Workers 16 years and over PLACE OF WORK Worked in state of residence Worked in county of residence": "Count, inside county",
    }

    loc_dicts = [{"city": city} for city in cities]
    loc_fips = [*map(name2fips, loc_dicts)]

    resp = await client.get_acs(
        vars=["S0801"], start_year=year, end_year=year, estimate="5", location=loc_fips
    )

    col_sub = [*list(cols.keys()), "state", "city"]
    resp = resp[col_sub]
    resp = resp.rename(columns=cols)

    ans = [
        ["Living/Working", resp.iloc[0]["city"].title()],
        [resp.columns[1], resp.iloc[0][1]],
        [resp.columns[2], resp.iloc[0][2]],
        [resp.columns[3], resp.iloc[0][3]],
    ]
    fig = ff.create_table(
        ans, colorscale=[[0, pri_color], [0.5, "#ffffff"], [1, "#ffffff"]]
    )

    fig.update_layout(font=dict(family="Glacial Indifference", size=18, color="black"))

    if save_path is not None:
        fig.write_image(
            save_path, height=img_height, width=img_width, scale=scale, format="png"
        )

    return fig


# ------------------------------
# Testing Code
# ------------------------------


async def main():
    client = ACSClient()
    try:
        await client.initialize()
        test = await households_with_internet(
            client=client, target_city="rancho mirage, ca"
        )
    finally:
        await client.close()
    test.show()

    # pop_growth_rates_year_groups().show()


if __name__ == "__main__":
    asyncio.run(main())
