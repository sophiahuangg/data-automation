# Code written by Aaron Xie, modified for script format by Abhi Uppal

import asyncio
import pandas as pd
import plotly.express as px

from lowe.locations.lookup import name2fips
from lowe.acs.ACSClient import ACSClient

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

# ------------------------------
# Helper Functions
# ------------------------------

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

# Fig 8: Total Household Income -- APPROVED


async def total_household_income(
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
    target_city: str = "desert hot springs ca",
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
    #     target_col = "INCOME IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS) Estimate Households Total"
    #     new_col_name = "Total Income"

    #     INCOME IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS) Estimate Families Total * INCOME IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS) Estimate Families Mean income (dollars)

    cols = {
        "INCOME IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS) Estimate Families Total": "Families Total",
        "INCOME IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS) Estimate Families Mean income (dollars)": "Income Per",
    }

    loc_dicts = [{"city": city} for city in cities]
    loc_fips = [*map(name2fips, loc_dicts)]

    resp = await client.get_acs(
        vars=["S1901"], start_year=year, end_year=year, estimate="5", location=loc_fips
    )

    col_sub = [*list(cols.keys()), "state", "city"]
    resp = resp[col_sub]
    resp = resp.rename(columns=cols)

    resp["Total Income"] = resp["Families Total"].astype(str).astype(int) * resp[
        "Income Per"
    ].astype(str).astype(int)

    # Following is unique to each section

    categ = resp["city"]
    value = resp["Total Income"]

    plot_df = pd.DataFrame({"city": categ, "Value": value})
    plot_df.city = plot_df.city.str.title()  # Capitalize first letter in each city

    # ISOLATING TARGET CITY
    city_list = plot_df["city"].values.tolist()
    city_index = city_list.index(target_city[0 : (len(target_city)) - 3].title())
    colors = [pri_color,] * len(cities)
    colors[city_index] = fund_ter

    fig = px.bar(
        plot_df,
        x="city",
        y="Value",
        text=plot_df["Value"].apply(lambda x: "{0:,.0f}".format(x)),
    )
    fig.update_xaxes(type="category")

    fig.update_layout(
        font_family="Glacial Indifference",
        font_color="black",
        title_font_family="Glacial Indifference",
        title_font_color="black",
        legend_title_font_color="black",
        template="plotly_white",
        yaxis_title="Total Household Income",
        font_size=18,
    )

    fig.update_traces(marker_color=colors, textposition='outside', width=0.5)

    if save_path is not None:
        fig.write_image(
            save_path, height=img_height, width=img_width, scale=scale, format="png"
        )

    return fig


# Fig 9: Median Household Income -- APPROVED


async def median_household_income(
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
    target_city: str = "desert hot springs ca",
    year: str = "2019",
    save_path: str = None,
    img_height: int = 1080,
    img_width: int = 1920,
    scale: int = 2,
):
    """
    DO NOT PASS CITIES PARAM (is a list of them); if one city just pass as list of 1
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
    target_col = "INCOME IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS) Estimate Families Median income (dollars)"
    new_col_name = "Median Income"

    loc_dicts = [{"city": city} for city in cities]
    loc_fips = [*map(name2fips, loc_dicts)]

    resp = await client.get_acs(
        vars=["S1901"], start_year=year, end_year=year, estimate="5", location=loc_fips
    )

    col_sub = [target_col, "state", "city"]
    resp = resp[col_sub]
    resp = resp.rename(columns={target_col: new_col_name})

    # Following is unique to each section

    categ = resp["city"]
    value = resp["Median Income"].astype(str).astype(int)

    plot_df = pd.DataFrame({"Type": categ, "Value": value})
    plot_df.Type = plot_df.Type.str.title()  # Capitalize first letter in each city

    # ISOLATING TARGET CITY
    city_list = plot_df["Type"].values.tolist()
    city_index = city_list.index(target_city[0 : (len(target_city)) - 3].title())
    colors = [pri_color,] * len(cities)
    colors[city_index] = fund_ter

    fig = px.bar(
        plot_df,
        x="Type",
        y="Value",
        text=plot_df["Value"].apply(lambda x: "{0:,.0f}".format(x)),
    )
    fig.update_xaxes(type="category")

    fig.update_layout(
        font_family="Glacial Indifference",
        font_color="black",
        title_font_family="Glacial Indifference",
        title_font_color="black",
        legend_title_font_color="black",
        template="plotly_white",
        xaxis_title="City",
        yaxis_title="Median Household Income",
        font_size=18,
    )

    fig.update_traces(marker_color=colors, textposition='outside', width=0.5)

    if save_path is not None:
        fig.write_image(
            save_path, height=img_height, width=img_width, scale=scale, format="png"
        )

    return fig


# Fig 10: Household Income By Class -- APPROVED


async def household_income_by_class(
    client: ACSClient,
    cities: list = ["coachella, ca", "desert hot springs, ca"],
    year: str = "2019",
    save_path: str = None,
    img_height: int = 1080,
    img_width: int = 1920,
    scale: int = 2,
):
    """
    DO NOT PASS CITIES PARAM (is a list of them); if one city just pass as list of 1
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
    # NOTE: &#36; is a $ -- needed in any label with 2 dollar signs. Without this, plotly tries to render it as LaTeX (math)
    cols = {
        # old col name: new name
        "INCOME IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS) Estimate Nonfamily households Total Less than $10,000": "Less than $10,000",
        "INCOME IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS) Estimate Nonfamily households Total $10,000 to $14,999": "&#36;10,000-&#36;14,999",
        "INCOME IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS) Estimate Nonfamily households Total $15,000 to $24,999": "&#36;15,000-&#36;24,999",
        "INCOME IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS) Estimate Nonfamily households Total $25,000 to $34,999": "&#36;25,000-&#36;34,999",
        "INCOME IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS) Estimate Nonfamily households Total $35,000 to $49,999": "&#36;35,000-&#36;49,999",
        "INCOME IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS) Estimate Nonfamily households Total $50,000 to $74,999": "&#36;50,000-&#36;74,999",
        "INCOME IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS) Estimate Nonfamily households Total $75,000 to $99,999": "&#36;75,000-&#36;99,999",
        "INCOME IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS) Estimate Nonfamily households Total $100,000 to $149,999": "&#36;100,000-&#36;149,999",
        "INCOME IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS) Estimate Nonfamily households Total $150,000 to $199,999": "&#36;150,000-&#36;199,999",
        "INCOME IN THE PAST 12 MONTHS (IN 2019 INFLATION-ADJUSTED DOLLARS) Estimate Nonfamily households Total $200,000 or more": "$200,000+",
    }

    loc_dicts = [{"city": city} for city in cities]
    loc_fips = [*map(name2fips, loc_dicts)]

    resp = await client.get_acs(
        vars=["S1901"], start_year=year, end_year=year, estimate="5", location=loc_fips
    )

    col_sub = [*list(cols.keys()), "state", "city"]
    resp = resp[col_sub]
    resp = resp.rename(columns=cols)

    # Following is unique to each section

    categ = resp.columns[0:10].astype(str)
    categ = _axis_line_breaks(categ, 10)
    bar_value = resp.iloc[1][0:10].astype(str).astype(float)
    line_value = resp.iloc[0][0:10].astype(str).astype(float)

    bar_df = pd.DataFrame({"Type": categ, "Percentage": bar_value})
    line_df = pd.DataFrame({"Type": categ, "Percentage": line_value})

    fig = px.line(
        line_df,
        x="Type",
        y="Percentage",
        color=px.Constant("Coachella Valley"),
        color_discrete_sequence=[sec_color],
    )
    fig.add_bar(
        x=bar_df["Type"],
        y=bar_df["Percentage"],
        name="Desert Hot Spring",
        text=bar_df["Percentage"].apply(lambda x: "{0:,.1f}%".format(x)),
    )

    fig.update_layout(
        font_family="Glacial Indifference",
        font_color="black",
        title_font_family="Glacial Indifference",
        title_font_color="black",
        legend_title_font_color="black",
        legend_title_text="Region",
        template="plotly_white",
        xaxis_title="City",
        yaxis_title="Percent of Households",
        font_size=18,
    )

    fig.update_traces(marker_color=pri_color, line=dict(width=3))

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
    await client.initialize()
    try:
        test = await household_income_by_class(client=client)
    finally:
        await client.close()
    test.show()
    return test


if __name__ == "__main__":
    asyncio.run(main())
