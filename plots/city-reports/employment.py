# Code written by Karan Goel, modifications for production made by Abhi Uppal
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Primary, secondary, and tertiary colors
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


def filter_df(city: str, df):
    """
    Filters df by city
    """
    df = df[df["City"].str.lower() == city.lower()]
    return df


def _find_first_industry(df: pd.DataFrame):
    """Finds the first industry column in a dataframe"""
    cols = list(df.columns)
    other_cols = ["city", "date"]
    for col in cols:
        if col.lower() not in other_cols:
            return col
    return None


def consolidate_industries(df: pd.DataFrame):
    """Returns a dataframe that has the 12 consolidated industries we want"""
    df["Logistics"] = (
        df["Wholesale Trade"] + df["Transportation and Warehousing"] + df["Utilities"]
    )
    df["FIRE"] = df["Finance and Insurance"] + df["Real Estate and Rental and Leasing"]
    df["Professional and Business Services"] = (
        df["Professional, Scientific, and Technical Services"]
        + df["Management of Companies and Enterprises"]
        + df["Administrative and Support and Waste Management and Remediation Services"]
    )
    df["Leisure and Hospitality"] = (
        df["Arts, Entertainment, and Recreation"]
        + df["Accommodation and Food Services"]
    )
    df["Education and Health Services"] = (
        df["Educational Services"] + df["Health Care and Social Assistance"]
    )
    df["Government"] = (
        df["Federal Government"] + df["State Government"] + df["Local Government"]
    )
    df["Mining and Natural Resources"] = (
        df["Mining, Quarrying, and Oil and Gas Extraction"]
        + df["Agriculture, Forestry, Fishing and Hunting"]
    )

    cols_to_select = [
        "DATE",
        "City",
        "Logistics",
        "Construction",
        "Manufacturing",
        "Retail Trade",
        "Information",
        "FIRE",
        "Professional and Business Services",
        "Leisure and Hospitality",
        "Education and Health Services",
        "Government",
        "Mining and Natural Resources",
        "Other Services (except Public Administration)",
    ]

    res = df[cols_to_select]
    return res


def preprocess_data(path: str):
    df = pd.read_csv(path, na_values=["***", ".", "NA"])
    # Pad the date and get it into datetime format
    df["DATE"] = df["DATE"].str.pad(width=6, side="left", fillchar="0")
    df["DATE"] = pd.to_datetime(df.DATE, format="%y-%b")
    df = df.fillna(0)
    return df


# ------------------------------
# Plot Generation
# ------------------------------

# Fig 14: Average Monthly Total Employment Per Year -- APPROVED


def avg_monthly_employment(
    city: str,
    data_path: str,
    save_path: str = None,
    img_height: int = 1080,
    img_width: int = 1920,
    scale: int = 2,
):
    """
    This function creates plots for the average monthly employment per year.
    """

    def plots(df):
        """
        Plots data using plotly
        """
        colname = "Average Monthly Employment"
        empl_data_plot = px.bar(
            df,
            x=df.index,
            y=colname,
            labels={"DATE": "Year"},
            text=df[colname].apply(lambda x: "{:,.0f}".format(x)),
        )
        empl_data_plot.update_traces(textposition="outside", marker_color=pri_color)
        empl_data_plot.update_layout(
            template="plotly_white",
            font=dict(family="Glacial Indifference", size=18, color="Black"),
            yaxis_title="Average Monthly Total Employment",
            xaxis_title="",
        )
        empl_data_plot.update_traces(textfont_size=16, width=0.5)
        return empl_data_plot

    # Read in and preprocess the data
    empl_data = preprocess_data(path=data_path)
    empl_data.set_index("DATE", inplace=True)

    # Calculate total employment, filter for city and resample to yearly
    empl_data["Total Employment"] = empl_data.loc[
        :, "Agriculture, Forestry, Fishing and Hunting":
    ].sum(axis=1)
    empl_data = empl_data[empl_data["Total Employment"] != 0]

    empl_data = filter_df(city, empl_data)
    empl_data = empl_data.resample("1Y").mean().round()
    empl_data.rename(
        columns={"Total Employment": "Average Monthly Employment"}, inplace=True
    )
    empl_data.index = empl_data.index.strftime("%Y")

    fig = plots(empl_data)
    if save_path is not None:
        fig.write_image(
            save_path, height=img_height, width=img_width, scale=scale, format="png"
        )

    return fig


# NEW FIGURE: Employment Compositions, Pandemic vs. Now -- APPROVED


def employment_composition_pandemic_now(
    city: str,
    data_path: str,
    save_path: str = None,
    img_height: int = 1080,
    img_width: int = 1920,
    scale: int = 2,
):
    def plots(df):
        df = df.set_index("DATE", drop=True)
        pandemic_shares = [df.loc[pandemic_date, x] for x in share_cols]
        recent_shares = [df.loc[most_recent_date, x] for x in share_cols]
        industry_names_to_plot = [*map(lambda x: x.split("_")[0], share_cols)]
        industry_names_to_plot = _axis_line_breaks(industry_names_to_plot, 10)

        dt_recent = datetime.datetime.strptime(most_recent_date, "%Y-%m-%d")
        dt_recent_str = dt_recent.strftime("%B %Y")

        dt_pandemic = datetime.datetime.strptime(pandemic_date, "%Y-%m-%d")
        dt_pandemic_str = dt_pandemic.strftime("%B %Y")

        fig = go.Figure(
            [
                go.Bar(
                    name=dt_pandemic_str,
                    x=industry_names_to_plot,
                    y=pandemic_shares,
                    text=[*map(lambda x: f"{x * 100:.1f}%", pandemic_shares)],
                    marker_color=fund_pri,
                ),
                go.Bar(
                    name=dt_recent_str,
                    x=industry_names_to_plot,
                    y=recent_shares,
                    text=[*map(lambda x: f"{x * 100:.1f}%", recent_shares)],
                    marker_color=fund_ter,
                ),
            ]
        )

        fig.update_layout(
            template="plotly_white",
            font=dict(family="Glacial Indifference", size=18, color="Black"),
            yaxis_title="Share of Total Employment",
            xaxis_title="",
            xaxis_tickangle=0,
        )

        fig.update_traces(textposition="outside", textfont_size=14)

        fig.update_xaxes(tickfont_size=16)

        return fig

    empl_data = preprocess_data(path=data_path)
    empl_data = filter_df(city, empl_data)
    empl_data = consolidate_industries(empl_data)
    empl_data = empl_data[empl_data["DATE"].dt.year >= 2020]

    empl_data["Total Employment"] = empl_data.iloc[:, 2:].sum(axis=1)

    empl_data = empl_data[empl_data["Total Employment"] != 0]

    # Get rid of any industries with zeros
    empl_data.replace(0, np.nan, inplace=True)
    empl_data.dropna(axis=1, inplace=True)

    cols = list(empl_data.columns)[2:]  # Leave out the City and Date columns
    share_cols = []

    for col in cols:
        if col != "Total Employment":
            share_name = f"{col}_share"
            empl_data[share_name] = empl_data[col] / empl_data["Total Employment"]
            share_cols.append(share_name)

    # Filter for the dates of interest
    empl_data["DATE"] = empl_data["DATE"].astype(str)
    pandemic_date = "2020-04-01"
    most_recent_date = empl_data.iloc[-1, :].loc["DATE"]

    pandemic_df = empl_data[empl_data["DATE"] == pandemic_date]
    recent_df = empl_data[empl_data["DATE"] == most_recent_date]

    empl_data = pd.concat([pandemic_df, recent_df])

    fig = plots(empl_data)

    if save_path is not None:
        fig.write_image(
            save_path, height=img_height, width=img_width, scale=scale, format="png"
        )
    return fig


# Figure 16: Employment Composition -- NOT USING


def employment_composition(
    city: str,
    data_path: str,
    save_path: str = None,
    img_height: int = 1080,
    img_width: int = 1920,
    scale: int = 2,
):
    def plots(df):
        """
        Plots data using plotly
        """
        colname = "Employment Share"
        empl_data_plot = px.bar(
            df,
            x=df.index,
            y=df["Employment Share"] * 100,
            labels={"index": "Employment Sector"},
            text=df[colname].apply(lambda x: "{:.1f}%".format(x * 100)),
        )
        empl_data_plot.update_traces(textposition="outside", marker_color=pri_color)
        empl_data_plot.update_layout(
            template="plotly_white",
            font=dict(family="Glacial Indifference", size=18, color="Black"),
            yaxis_title="Share of Total Employment",
        )
        return empl_data_plot

    # Read in and preprocess the data
    empl_data = preprocess_data(path=data_path)
    empl_data = filter_df(city, empl_data)
    empl_data = consolidate_industries(empl_data)
    empl_data = empl_data[empl_data["DATE"].dt.year > 2020]
    empl_data = empl_data[empl_data["DATE"].dt.month == 3]
    empl_data["Total Employment"] = empl_data.iloc[:, 2:].sum(axis=1)
    for sector in empl_data.columns[2:]:
        empl_data[sector + " "] = empl_data[sector] / empl_data["Total Employment"]

    # Calculate employment shares
    empl_share_df = pd.DataFrame()
    empl_share_df.index = empl_data.columns[14:]
    empl_share_df["Employment Share"] = empl_data.iloc[0, 14:]
    empl_share_df = empl_share_df.drop(index="Total Employment ")
    empl_share_df = empl_share_df.sort_values("Employment Share", ascending=False)

    fig = plots(empl_share_df)
    if save_path is not None:
        fig.write_image(
            save_path, height=img_height, width=img_width, scale=scale, format="png"
        )
    return fig


# Figure 17: Change in Employment Composition -- NOT USING


def change_employment_composition(
    city: str,
    data_path: str,
    save_path: str = None,
    img_height: int = 1080,
    img_width: int = 1920,
    scale: int = 2,
):
    def plots(df):
        colname = "Change in Employment Share"
        empl_data_plot = px.bar(
            df,
            x=df.index,
            y=colname,
            labels={"index": "Sector"},
            text=df[colname].apply(lambda x: "{:.1f}%".format(x)),
        )
        empl_data_plot.update_traces(textposition="outside", marker_color=pri_color)
        empl_data_plot.update_layout(
            template="plotly_white",
            font=dict(family="Glacial Indifference", size=18, color="Black"),
            yaxis_title=colname + " (Percentage Pts.)",
        )
        return empl_data_plot

    # Read in and preprocess the data
    empl_data = preprocess_data(path=data_path)
    empl_data = filter_df(city, empl_data)
    empl_data = consolidate_industries(empl_data)
    empl_data = empl_data[empl_data["DATE"].dt.year > 2019]
    empl_data = empl_data[empl_data["DATE"].dt.month == 3]

    empl_data["Total Employment"] = empl_data.iloc[:, 2:].sum(axis=1)
    for sector in empl_data.columns[2:]:
        empl_data[sector + " "] = empl_data[sector] / empl_data["Total Employment"]
    change_df = pd.DataFrame()
    change_df.index = empl_data.columns[2:]
    change_df["Change in Employment Share"] = (
        empl_data.iloc[0, 14:] - empl_data.iloc[1, 14:]
    )
    change_df = change_df[change_df["Change in Employment Share"] != 0.0]
    change_df = change_df.dropna()
    change_df["Change in Employment Share"] = (
        change_df["Change in Employment Share"] * 100
    )
    fig = plots(change_df)

    if save_path is not None:
        fig.write_image(
            save_path, height=img_height, width=img_width, scale=scale, format="png"
        )


# Fig 18: Change in Employment share from Previous peak by Sector -- NOT USING


def change_empl_share_prev_peak_per_sector(
    city: str,
    data_path: str,
    save_path_abs: str = None,
    save_path_perc: str = None,
    img_height: int = 1080,
    img_width: int = 1920,
    scale: int = 2,
):
    def plots(df):
        """
        Plots data using plotly
        """
        industries = list(df["INDUSTRY"])
        fig = go.Figure(
            [
                go.Bar(
                    name="Gain From Previous Peak",
                    x=industries,
                    y=df["netgain"],
                    marker_color="lightgreen",
                ),
                go.Bar(
                    name="Remaining Loss From Previous Peak",
                    x=industries,
                    y=df["remaining"],
                    marker_color="red",
                ),
                go.Bar(
                    name="Recovery Since Peak",
                    x=industries,
                    y=df["recovery"],
                    marker_color="darkblue",
                ),
            ]
        )
        fig.update_layout(
            template="plotly_white",
            font=dict(family="Glacial Indifference", size=18, color="Black"),
            yaxis_title="Change in Employment Share",
            xaxis_title="Industry",
            barmode="relative",
        )

        fig2 = go.Figure(
            [
                go.Bar(
                    name="Gain From Previous Peak",
                    x=industries,
                    y=df["netgain_perc"],
                    marker_color="lightgreen",
                ),
                go.Bar(
                    name="Remaining Loss From Previous Peak",
                    x=industries,
                    y=df["remaining_perc"],
                    marker_color="red",
                ),
                go.Bar(
                    name="Recovery Since Peak",
                    x=industries,
                    y=df["recovery_perc"],
                    marker_color="darkblue",
                ),
            ]
        )
        fig2.update_layout(
            template="plotly_white",
            font=dict(family="Glacial Indifference", size=18, color="Black"),
            yaxis_title="Percent Change in Employment Share",
            xaxis_title="Industry",
            barmode="relative",
        )

        return fig, fig2

    # Read in and preprocess the data
    empl_data = preprocess_data(path=data_path)
    empl_data = filter_df(city, empl_data)
    empl_data = consolidate_industries(empl_data)
    empl_data = empl_data.set_index("DATE")

    empl_data["Total Employment"] = empl_data.iloc[:, 2:].sum(axis=1)
    for sector in empl_data.columns[2:]:
        empl_data[sector + " "] = empl_data[sector] / empl_data["Total Employment"]
    empl_share_df = empl_data.drop(columns=empl_data.columns[2:14])

    max_frame = empl_share_df.loc["2013-01-01":"2020-03-01", :]
    min_frame = empl_share_df.loc["2020-03-01":, :]
    industryCols = empl_share_df.columns[2:]

    now = empl_share_df.iloc[-1, :]

    maxes = []
    mins = []
    now_vals = []
    for col in industryCols:
        maxes.append(max_frame[col].max())
        mins.append(min_frame[col].min())
        now_vals.append(now[col])

    graph_df = pd.DataFrame(
        {"INDUSTRY": industryCols, "MAX": maxes, "MIN": mins, "NOW": now_vals}
    )

    remaining = []
    recovery = []
    netgain = []

    for idx, item in graph_df.iterrows():
        if item["NOW"] < item["MAX"]:
            remaining.append(item["NOW"] - item["MAX"])
            netgain.append(0)
            recovery.append(item["MIN"] - item["NOW"])
        else:
            remaining.append(0)
            netgain.append(item["NOW"] - item["MAX"])
            recovery.append(item["MIN"] - item["MAX"])

    graph_df["remaining"] = remaining
    graph_df["recovery"] = recovery
    graph_df["netgain"] = netgain

    graph_df["remaining_perc"] = graph_df["remaining"] / graph_df["MAX"]
    graph_df["recovery_perc"] = graph_df["recovery"] / graph_df["MAX"]
    graph_df["netgain_perc"] = graph_df["netgain"] / graph_df["MAX"]

    graph_df = graph_df[:-1]
    # print(empl_data)
    fig_abs, fig_perc = plots(graph_df)

    if save_path_abs is not None and save_path_perc is not None:
        fig_abs.write_image(
            save_path_abs, height=img_height, width=img_width, scale=scale, format="png"
        )
        fig_perc.write_image(
            save_path_perc,
            height=img_height,
            width=img_width,
            scale=scale,
            format="png",
        )

    return fig_abs, fig_perc


# Fig 19, 20: Change in Employment, Peak to Trough, Absolute and Percentages -- WIP


def peak_to_trough_empl(
    data_path: str,
    city: str,
    save_path_abs: str = None,
    save_path_perc: str = None,
    img_height: int = 1080,
    img_width: int = 1920,
    scale: int = 2,
):
    def plots(df):
        """
        Plots data using plotly
        """
        industries = list(df["INDUSTRY"])
        fig = go.Figure(
            [
                go.Bar(
                    name="Gain From Previous Peak",
                    x=industries,
                    y=df["netgain"],
                    marker_color="green",
                ),
                go.Bar(
                    name="Remaining Loss From Previous Peak",
                    x=industries,
                    y=df["remaining"],
                    marker_color=pri_color,
                ),
                go.Bar(
                    name="Recovery Since Peak",
                    x=industries,
                    y=df["recovery"],
                    marker_color="darkblue",
                ),
            ]
        )
        fig.update_layout(
            template="plotly_white",
            font=dict(family="Glacial Indifference", size=18, color="Black"),
            yaxis_title="Change in Employment",
            xaxis_title="Industry",
            barmode="relative",
        )

        fig2 = go.Figure(
            [
                go.Bar(
                    name="Gain From Previous Peak",
                    x=industries,
                    y=df["netgain_perc"],
                    marker_color="green",
                ),
                go.Bar(
                    name="Remaining Loss From Previous Peak",
                    x=industries,
                    y=df["remaining_perc"],
                    marker_color=pri_color,
                ),
                go.Bar(
                    name="Recovery Since Peak",
                    x=industries,
                    y=df["recovery_perc"],
                    marker_color="darkblue",
                ),
            ]
        )
        fig2.update_layout(
            template="plotly_white",
            font=dict(family="Glacial Indifference", size=18, color="Black"),
            yaxis_title="Percent Change in Employment",
            xaxis_title="Industry",
            barmode="relative",
        )

        return fig, fig2

    # Read in the employment data
    empl = pd.read_csv(data_path, na_values=["***", ".", "NA"])
    empl["DATE"] = empl["DATE"].str.pad(width=6, side="left", fillchar="0")
    empl["Total"] = empl.loc[:, "Agriculture, Forestry, Fishing and Hunting":].sum(
        axis=1
    )
    empl["DATE"] = pd.to_datetime(empl.DATE, format="%y-%b")
    empl["City"] = empl["City"].str.lower()
    empl = empl.fillna(0)

    empl_c = consolidate_industries(empl)
    # Filter for the city
    city = empl_c[empl_c["City"] == city.lower()]
    city["Total"] = city.loc[:, "Logistics":].sum(axis=1)

    # Set the index to be a datetime index and get rid of empty rows
    city = city.set_index("DATE")
    city = city[city["Total"] != 0]

    # Get the present value for each industry and note which
    now = city.iloc[-1, :]

    # Get rid of any industries that have no present workers
    cols_to_drop = []
    for idx, item in now.iteritems():
        try:
            item = int(item)
            if item == 0:
                cols_to_drop.append(idx)
        except ValueError:
            continue
    city = city.drop(columns=cols_to_drop + ["Total"])
    firstCol = _find_first_industry(city)
    industryCols = city.loc[:, firstCol:].columns

    # Get dataframes to calculate the max and min for each industry
    max_frame = city.loc["2013-01-01":"2020-03-01", :]
    min_frame = city.loc["2020-03-01":, :]

    maxes = []
    mins = []
    now_vals = []
    for col in industryCols:
        maxes.append(max_frame[col].max())
        mins.append(min_frame[col].min())
        now_vals.append(now[col])

    graph_df = pd.DataFrame(
        {"INDUSTRY": industryCols, "MAX": maxes, "MIN": mins, "NOW": now_vals}
    )

    # Add columns to graph_df for the plot
    remaining = []
    recovery = []
    netgain = []

    for idx, item in graph_df.iterrows():
        if item["NOW"] < item["MAX"]:
            remaining.append(item["NOW"] - item["MAX"])
            netgain.append(0)
            recovery.append(item["MIN"] - item["NOW"])
        else:
            remaining.append(0)
            netgain.append(item["NOW"] - item["MAX"])
            recovery.append(item["MIN"] - item["MAX"])

    graph_df["remaining"] = remaining
    graph_df["recovery"] = recovery
    graph_df["netgain"] = netgain

    graph_df["remaining_perc"] = graph_df["remaining"] / graph_df["MAX"]
    graph_df["recovery_perc"] = graph_df["recovery"] / graph_df["MAX"]
    graph_df["netgain_perc"] = graph_df["netgain"] / graph_df["MAX"]

    fig_abs, fig_perc = plots(graph_df)

    if save_path_abs is not None and save_path_perc is not None:
        fig_abs.write_image(
            save_path_abs, height=img_height, width=img_width, scale=scale, format="png"
        )
        fig_perc.write_image(
            save_path_perc,
            height=img_height,
            width=img_width,
            scale=scale,
            format="png",
        )

    return fig_abs, fig_perc


def main():
    test = employment_composition_pandemic_now(
        city="Cathedral City", data_path="data/CV_EMPL.csv"
    )
    if not isinstance(test, pd.DataFrame):
        test.show()
    else:
        print(test)


if __name__ == "__main__":
    main()
