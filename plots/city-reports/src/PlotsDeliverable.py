from lowe.locations.lookup import search, generate_df_json
from lowe.acs.ACSClient import ACSClient
import pandas as pd
import plotly.graph_objects as go


async def humanCapitalIndexCV(
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
    target_city: str = "desert hot springs, ca",
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
    all_loc = []

    for city in cities:
        df = generate_df_json(codetype="city")
        df = df.astype(str)  # Convert all cols to string
        # df[df['A'].str.contains("hello")]
        df = df[df["name"].str.contains(city)]
        fips = df.iloc[0]["fips"]

        loc = {"state": fips[0:2], "city": fips[2:]}
        all_loc.append(loc)

    client = ACSClient()
    await client.initialize()

    resp = await client.get_acs(
        vars=["S1501"],
        start_year="2019",
        end_year="2019",
        location=all_loc,
        estimate="5",
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

    renamed_colsDict = {
        "EDUCATIONAL ATTAINMENT Estimate Percent AGE BY EDUCATIONAL ATTAINMENT Population 25 years and over Less than 9th grade": "Less than 9th grade",
        "EDUCATIONAL ATTAINMENT Estimate Percent AGE BY EDUCATIONAL ATTAINMENT Population 25 years and over 9th to 12th grade, no diploma": "9th to 12th grade, no diploma",
        "EDUCATIONAL ATTAINMENT Estimate Percent AGE BY EDUCATIONAL ATTAINMENT Population 25 years and over High school graduate (includes equivalency)": "High school graduate (includes equivalency)",
        "EDUCATIONAL ATTAINMENT Estimate Percent AGE BY EDUCATIONAL ATTAINMENT Population 25 years and over Some college, no degree": "Some college, no degree",
        "EDUCATIONAL ATTAINMENT Estimate Percent AGE BY EDUCATIONAL ATTAINMENT Population 25 years and over Associate's degree": "Associate's degree",
        "EDUCATIONAL ATTAINMENT Estimate Percent AGE BY EDUCATIONAL ATTAINMENT Population 25 years and over Bachelor's degree": "Bachelor's degree",
        "EDUCATIONAL ATTAINMENT Estimate Percent AGE BY EDUCATIONAL ATTAINMENT Population 25 years and over Graduate or professional degree": "Graduate or professional degree",
    }
    renamed_colsList = [
        "Less than 9th grade",
        "9th to 12th grade, no diploma",
        "High school graduate (includes equivalency)",
        "Some college, no degree",
        "Associate's degree",
        "Bachelor's degree",
        "Graduate or professional degree",
    ]

    df_resp = resp[target_cols]
    df_resp = df_resp.apply(pd.to_numeric, errors="ignore")
    df_resp = df_resp.rename(columns=renamed_colsDict)  # memorize this
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
        "#e6aeb7",
    ] * 9
    colors[list(df_resp["city"]).index(target_city.title())] = "#c5485f"

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
        title=dict(
            text="Human Capital Index, Cities of the Coachella Valley, 2019",
            yanchor="top",
            y=0.9,
            xanchor="center",
            x=0.5,
        ),
        template="plotly_white",
        font=dict(family="Old-style", size=14, color="Black")
        #     yaxis = dict(tickformat = lambda x: '{0:1.1f}%'.format(x), range = [0,100])
    )
    fig.show()

    if save:
        fig.write_image(save_path)
    return fig


async def educationalAttainmentCV(
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
    all_loc = []

    for city in cities:
        df = generate_df_json(codetype="city")
        df = df.astype(str)  # Convert all cols to string
        # df[df['A'].str.contains("hello")]
        df = df[df["name"].str.contains(city)]
        fips = df.iloc[0]["fips"]

        loc = {"state": fips[0:2], "city": fips[2:]}
        all_loc.append(loc)

    client = ACSClient()
    await client.initialize()

    resp = await client.get_acs(
        vars=["S1501"],
        start_year="2019",
        end_year="2019",
        location=all_loc,
        estimate="5",
    )

    # important columns and dictionaries below:

    target_cols = [
        "EDUCATIONAL ATTAINMENT Estimate Percent AGE BY EDUCATIONAL ATTAINMENT Population 25 years and over High school graduate or higher",
        "EDUCATIONAL ATTAINMENT Estimate Percent AGE BY EDUCATIONAL ATTAINMENT Population 25 years and over Bachelor's degree or higher",
        "city",
        "state",
        "location_key",
    ]

    renamed_cols = {
        "EDUCATIONAL ATTAINMENT Estimate Percent AGE BY EDUCATIONAL ATTAINMENT Population 25 years and over High school graduate or higher": "High School Ed. Attainment",
        "EDUCATIONAL ATTAINMENT Estimate Percent AGE BY EDUCATIONAL ATTAINMENT Population 25 years and over Bachelor's degree or higher": "College Ed. Attainment",
    }

    new_cols = ["High School Ed. Attainment", "College Ed. Attainment"]

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
            marker_color="#c5485f",
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
            marker_color="#e6aeb7",
            name="College",
            text=College.apply(lambda x: "{0:1.1f}%".format(x)),
            textposition="outside",
        )
    )

    # Change the bar mode
    fig.update_layout(barmode="group")
    fig.update_layout(
        title=dict(
            text="Educational Attainment, Coachella Valley, 2019",
            yanchor="top",
            y=0.9,
            xanchor="center",
            x=0.5,
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.17, xanchor="center", x=0.47
        ),
        template="plotly_white",
        font=dict(family="Old-style", size=14, color="Black"),
        yaxis=dict(tickformat=".0%", hoverformat="closest"),
    )
    fig.show()

    # option for saving
    if save:
        fig.write_image(save_path)
    return fig


async def healthInsuranceCity(
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
    save: bool = False,
    save_path: str = None,
):
    """
    Parameters
    ----------
    city: name of the city as a list eg. ['cathedral city, ca'] or ['coachella, ca'] etc.
    save: bool
    True or False, whether or not you want to save
    save_path: str
    Path to save the file to
    """

    all_loc = []

    for city in cities:
        df = generate_df_json(codetype="city")
        df = df.astype(str)  # Convert all cols to string
        # df[df['A'].str.contains("hello")]
        df = df[df["name"].str.contains(city)]
        fips = df.iloc[0]["fips"]

        loc = {"state": fips[0:2], "city": fips[2:]}

    all_loc.append(loc)

    client = ACSClient()
    await client.initialize()

    # pull data for city passed in
    resp = await client.get_acs(
        vars=["S2701"],
        start_year="2015",
        end_year="2019",
        location=all_loc,
        estimate="5",
    )

    # pull data for united states
    resp1 = await client.get_acs(
        vars=["S2701"],
        start_year="2015",
        end_year="2019",
        location={},  # united states
        estimate="5",
    )

    # pull data for california
    resp2 = await client.get_acs(
        vars=["S2701"],
        start_year="2015",
        end_year="2019",
        location={"state": "06"},  # california
        estimate="5",
    )

    target_cols = [
        "SELECTED CHARACTERISTICS OF HEALTH INSURANCE COVERAGE IN THE UNITED STATES Estimate Percent Insured Civilian noninstitutionalized population",
        "location_key",
    ]

    renamed_colCalifornia = {
        "SELECTED CHARACTERISTICS OF HEALTH INSURANCE COVERAGE IN THE UNITED STATES Estimate Percent Insured Civilian noninstitutionalized population": "California"
    }
    renamed_colCity = {
        "SELECTED CHARACTERISTICS OF HEALTH INSURANCE COVERAGE IN THE UNITED STATES Estimate Percent Insured Civilian noninstitutionalized population": city.title()
    }
    renamed_colUS = {
        "SELECTED CHARACTERISTICS OF HEALTH INSURANCE COVERAGE IN THE UNITED STATES Estimate Percent Insured Civilian noninstitutionalized population": "United States"
    }

    # format city dataframe
    df_resp = resp[target_cols]
    df_resp = df_resp.apply(pd.to_numeric, errors="ignore")
    df_resp = df_resp.rename(columns=renamed_colCity)  # memorize this
    df_resp  # city

    # format us dataframe
    df_resp1 = resp1[target_cols]
    df_resp1 = df_resp1.apply(pd.to_numeric, errors="ignore")
    df_resp1 = df_resp1.rename(columns=renamed_colUS)  # memorize this
    df_resp1

    # format california dataframe
    df_resp2 = resp2[target_cols]
    df_resp2 = df_resp2.apply(pd.to_numeric, errors="ignore")
    df_resp2 = df_resp2.rename(columns=renamed_colCalifornia)  # memorize this
    df_resp2

    # combine all three dataframes

    df_final = pd.concat([df_resp[city.title()], df_resp1["United States"]], axis=1)
    df_final = pd.concat([df_final, df_resp2["California"]], axis=1)
    df_final

    # plot data
    fig = px.line()

    fig.add_trace(
        go.Scatter(
            x=df_final.index,
            y=df_final[city.title()] / 100,
            #                          mode = 'line+markers',
            name=city.title(),
            line=dict(color="#961a30"),
            text=df_final[city.title()].apply(lambda x: "{0:1.1f}%".format(x)),
            mode="lines+markers+text",
            textposition="top center",
            legendrank=3,
            textfont=dict(family="Old-style", size=14, color="#961a30"),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_final.index,
            y=df_final["California"] / 100,
            name="California",
            line=dict(color="#c5485f"),
            #                              text= df_final['California'].apply(lambda x: '{0:1.1f}%'.format(x)),
            #                              mode="lines+markers+text",
            #                              textposition = 'top center',
            legendrank=2,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_final.index,
            y=df_final["United States"] / 100,
            name="United States",
            line=dict(color="#e6aeb7"),
            #                              text= df_final['United States'].apply(lambda x: '{0:1.1f}%'.format(x)),
            #                              textposition = 'bottom center',
            #                              mode="lines+markers+text",
            legendrank=1,
        )
    )

    fig.update_xaxes(dtick="M1", tickformat="%b\n%Y", ticklabelmode="period")

    fig.update_layout(
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5
        ),
        title=f"Percentage of Population with Health Insurance, {city.title()}, CA, and U.S., 2015-2019",
        template="plotly_white",
        font=dict(family="Old-style", size=14, color="Black"),
        yaxis=dict(tickformat=".0%", hoverformat="closest"),
    )

    fig.show()

    if save:
        fig.write_image(save_path)
    return fig
