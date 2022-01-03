# Code written by Aaron Onate, slight modifications for production made by Abhi Uppal

import asyncio
import pandas as pd
import plotly.graph_objects as go

from lowe.acs.ACSClient import ACSClient
from lowe.locations.lookup import name2fips

# Primary and secondary colors
pri_color = "#961a30"
sec_color = "#e7c8ae"
ter_color = "#e6aeb7"


# ------------------------------
# Plot Generation
# ------------------------------

# Fig 25: Total Household Income -- APPROVED


async def human_capital_index_cv(
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
    target_city: str = "desert hot springs",
    year: str = "2019",
    save: bool = False,
    save_path: str = None,
):
    """
    Parameters
    ----------
    cities: list of all the names of the cities in coachella valley
    target_city: the city you want to highlight in the bar graph **DONT INCLUDE THE STATE**
        i.e. 'coachella' or 'palm desert' etc
        NOT 'coachella, ca'

    save: bool
    True or False, whether or not you want to save
    save_path: str
    Path to save the file to
    """
    loc_dicts = [{"city": city} for city in cities]
    locs = [*map(name2fips, loc_dicts)]

    resp = await client.get_acs(
        vars=["S1501"], start_year=year, end_year=year, estimate="5", location=locs
    )

    target_cols = [
        "EDUCATIONAL ATTAINMENT Estimate Percent AGE BY EDUCATIONAL ATTAINMENT Population 25 years and over Less than 9th grade",
        "EDUCATIONAL ATTAINMENT Estimate Percent AGE BY EDUCATIONAL ATTAINMENT Population 25 years and over 9th to 12th grade, no diploma",
        "EDUCATIONAL ATTAINMENT Estimate Percent AGE BY EDUCATIONAL ATTAINMENT Population 25 years and over High school graduate (includes equivalency)",
        "EDUCATIONAL ATTAINMENT Estimate Percent AGE BY EDUCATIONAL ATTAINMENT Population 25 years and over Some college, no degree",
        "EDUCATIONAL ATTAINMENT Estimate Percent AGE BY EDUCATIONAL ATTAINMENT Population 25 years and over Associate's degree",
        "EDUCATIONAL ATTAINMENT Estimate Percent AGE BY EDUCATIONAL ATTAINMENT Population 25 years and over Bachelor's degree",
        "EDUCATIONAL ATTAINMENT Estimate Percent AGE BY EDUCATIONAL ATTAINMENT Population 25 years and over Graduate or professional degree",
        "city",
    ]

    renamed_colsList = [
        "Less than 9th grade",
        "9th to 12th grade, no diploma",
        "High school graduate (includes equivalency)",
        "Some college, no degree",
        "Associate's degree",
        "Bachelor's degree",
        "Graduate or professional degree",
    ]

    renamed_colsDict = dict(zip(target_cols, renamed_colsList))

    df_resp = resp[target_cols]
    df_resp = df_resp.apply(pd.to_numeric, errors="ignore")
    df_resp = df_resp.rename(columns=renamed_colsDict)
    df_resp["city"] = df_resp["city"].apply(lambda x: x.title())

    # applying the weights to each column
    weights = [50, 100, 120, 130, 140, 160, 180]

    for i in range(len(weights)):
        df_resp[renamed_colsList[i]] = df_resp[renamed_colsList[i]] * weights[i]

    df_resp["HCI"] = df_resp.sum(axis=1) / 100
    df_resp = df_resp.sort_values("HCI", ascending=False)

    # plotting the dataframe
    HCI = df_resp["HCI"]
    cities = df_resp["city"]

    # set the colors
    colors = [
        pri_color,
    ] * 9
    colors[list(df_resp["city"]).index(target_city.title())] = sec_color

    # build the figure
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            name="High School",
            x=cities,
            y=HCI,
            text=HCI.apply(lambda x: "{0:1.1f}".format(x)),
            textposition="outside",
            marker_color=colors,
        )
    )

    # Change the bar mode
    fig.update_traces(texttemplate="", textposition="outside")
    fig.update_layout(
        yaxis_title=f"Human Capital Index, {year}",
        template="plotly_white",
        font=dict(family="Glacial Indifference", size=14, color="Black"),
    )

    if save:
        fig.write_image(save_path)
    return fig


# Fig 26: Educational Attainment Levels -- WIP


async def educational_attainment_cv(
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
    Parameters
    ----------
    cities: cities in coachella valley as a list
    save: bool
    True or False, whether or not you want to save
    save_path: str
    Path to save the file to
    """
    loc_dicts = [{"city": city} for city in cities]
    locs = [*map(name2fips, loc_dicts)]

    resp = await client.get_acs(
        vars=["S1501"], start_year=year, end_year=year, estimate="5", location=locs
    )

    # important columns and dictionaries below:

    target_cols = [
        "EDUCATIONAL ATTAINMENT Estimate Percent AGE BY EDUCATIONAL ATTAINMENT Population 25 years and over High school graduate or higher",
        "EDUCATIONAL ATTAINMENT Estimate Percent AGE BY EDUCATIONAL ATTAINMENT Population 25 years and over Bachelor's degree or higher",
        "city",
        "state",
        "location_key",
    ]

    new_cols = ["High School Ed. Attainment", "College Ed. Attainment"]

    renamed_cols = dict(zip(target_cols, new_cols))

    # restructuring final dataframe

    df_final = resp[target_cols]
    df_final = df_final.rename(columns=renamed_cols)

    df_final = df_final.apply(pd.to_numeric, errors="ignore")
    df_final = df_final.sort_values("High School Ed. Attainment", ascending=False)
    df_final = df_final.sort_values("College Ed. Attainment", ascending=False)
    df_final["city"] = df_final["city"].apply(lambda x: x.title())
    df_final

    # plotting dataframe
    cities = df_final["city"]
    College = df_final["College Ed. Attainment"]
    high_School = df_final["High School Ed. Attainment"]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=cities,
            y=high_School / 100,
            base=0,
            marker_color=pri_color,
            name="High School",
            text=high_School.apply(lambda x: "{0:1.1f}%".format(x)),
            textposition="outside",
        )
    )

    fig.add_trace(
        go.Bar(
            x=cities,
            y=College / 100,
            base=0,
            marker_color=ter_color,
            name="College",
            text=College.apply(lambda x: "{0:1.1f}%".format(x)),
            textposition="outside",
        )
    )

    # Change the bar mode
    fig.update_layout(barmode="group")
    fig.update_layout(
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.17, xanchor="center", x=0.47
        ),
        template="plotly_white",
        font=dict(family="Glacial Indifference", size=14, color="Black"),
        yaxis=dict(tickformat=".0%", hoverformat="closest"),
        yaxis_title="Percent of Population 25+ Years Old",
    )

    # option for saving
    if save:
        fig.write_image(save_path)
    return fig


# ------------------------------
# Testing Code
# ------------------------------


async def main():
    client = ACSClient()
    await client.initialize()
    try:
        test = await educational_attainment_cv(client=client)
    finally:
        await client.close()
    test.show()
    return test


if __name__ == "__main__":
    asyncio.run(main())
