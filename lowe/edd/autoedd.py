import datetime as dt
import numpy as np
import pandas as pd

from bidict import bidict
from typing import Union


def _load_msa(fname: str = "data/RIVE$HWS.xlsx", melted: bool = True):
    """Helper function to load and preprocess the data for a particular MSA"""
    # Read in the data
    df = pd.read_excel(fname, skiprows=7, skipfooter=9)
    cols = df.columns

    # Gather all of the dates into one column
    if melted:
        df = pd.melt(df, id_vars=[cols[i] for i in range(8)])
        mapper = {"variable": "time"}
        df.rename(
            mapper=mapper,
            axis=1,
            inplace=True,
        )

    # Make sure the output is in datetime format

    if melted:
        df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%d")

    return df


def _colname_to_str(colname):
    """
    Converts datetime column names to string repr in the format:
    Apr-20 -- that is, '%b-%y'
    """
    # See https://strftime.org/

    if isinstance(colname, dt.datetime):
        colname = colname.strftime(format="%b-%y")
    return colname


def _range_to_int_list(rng: str):
    """Converts string in format num1:num2 to a list of integers"""
    if ":" in rng:
        splt = rng.split(":")
        start = splt[0]
        end = splt[1]

        lst = list(range(int(start), int(end) + 1))

        return lst
    return rng


def _year_avg(
    df: pd.DataFrame,
    year: Union[int, str],
    start_month: str = "Jan",
    end_month: str = "Dec",
):
    """_year_avg averages the vectors for an unmelted dataframe for the specified year from the starting month to the ending month

    Parameters
    ----------
    df : pd.DataFrame
        unmelted dataframe to get data from
    year : Union[int, str]
        year to average over
    start_month : str, optional
        Month to begin averaging at in 3-letter format, by default "Jan"
    end_month : str, optional
        Month to end averaging at in 3-letter format, by default "Dec"
    """
    year = str(year)
    if len(year) == 4:  # If we pass in "2020" for example
        year = year[-2:]  # Take the last two digits

    cols = df.loc[:, f"{start_month}-{year}":f"{end_month}-{year}"]

    return cols.sum(axis=1) / len(cols)


def _naics_level(code: str) -> int:
    """_naics_level is a helper that allows us to determine what level the employment sector is talking about

    Parameters
    ----------
    code : str
        NAICS Sector as a string in the format xx-xxxxxx

    Returns
    -------
    int: The number corresponding to the level of the NAICS sector
    """
    codestr = code.split("-")[-1]  # Get the part of the string we care about
    return (
        len(codestr) - (codestr.count("0")) + 2
    )  # The first two digits will always be counted


def _kleinhenz_process(fname: str = "data/RIVE$HWS.xlsx"):
    """_kleinhenz_process produces the variables Dr. Kleinhenz has us use for the EDD news releases

    Parameters
    ----------
    fname : str
        Filename containing the EDD data we want to process
    """

    # Load and preprocess

    df = _load_msa(fname=fname, melted=False)
    df.columns = [_colname_to_str(col) for col in df.columns]

    indices = {df.columns.get_loc(c): c for idx, c in enumerate(df.columns)}
    inv = bidict(indices).inverse
    cols_of_interest = [
        "SS-NAICS",
        "TITLE",
        "Jan-19",
    ]
    idxs = [inv[col] for col in cols_of_interest]
    idxs[-1] = str(idxs[-1]) + f":{len(df.columns) - 1}"
    rng = _range_to_int_list(idxs[-1])
    idxs = idxs[0:-1] + rng

    df = df.iloc[:, idxs]

    # Generate new columns

    # Year to year change processing

    current = df.columns[-1]
    split_current = current.split("-")
    month, year = split_current[0], split_current[1]
    last_year_colname = f"{month}-{str(int(year) - 1)}"

    MTM = df.iloc[:, -1] - df.iloc[:, -2]
    MTM_PERC = (df.iloc[:, -1] / df.iloc[:, -2]) - 1
    YTY = df.iloc[:, -1] - df[last_year_colname]
    YTY_PERC = (df.iloc[:, -1] / df[last_year_colname]) - 1
    NOW_MINUS_FEB = df.iloc[:, -1] - df["Feb-20"]
    NOW_MINUS_FEB_PERC = (df.iloc[:, -1] / df["Feb-20"]) - 1
    APR_MINUS_FEB_2020 = df["Apr-20"] - df["Feb-20"]
    APR_MINUS_FEB_2020_PERC = (df["Apr-20"] / df["Feb-20"]) - 1
    RECOVERY = df.iloc[:, -1] - df["Apr-20"]  # Now - Apr 2020
    RECOVERY_PERC = RECOVERY / (-1 * APR_MINUS_FEB_2020)
    NOW_AS_OF_FEB_2020 = df.iloc[:, -1] / df["Feb-20"]
    YTD_2020 = _year_avg(df, "2020", end_month="Jul")
    YTD_2021 = _year_avg(df, "2021", end_month="Jul")
    CHG = YTD_2021 - YTD_2020
    CHG_PERC = YTD_2021 / YTD_2020 - 1
    AVG_2019 = _year_avg(df, "2019")
    AVG_2020 = _year_avg(df, "2020")
    DIFF_AVG = AVG_2020 - AVG_2019
    DIFF_AVG_PERC = (AVG_2020 / AVG_2019) - 1

    df["Industry Level"] = df["SS-NAICS"].apply(_naics_level)
    df["MTM"] = MTM
    df["MTM%"] = MTM_PERC
    df["YTY"] = YTY
    df["YTY%"] = YTY_PERC
    df["now minus feb 2020"] = NOW_MINUS_FEB
    df["now minus feb 2020%"] = NOW_MINUS_FEB_PERC
    df["apr 2020 minus feb 2020"] = APR_MINUS_FEB_2020
    df["apr 2020 minus feb 2020%"] = APR_MINUS_FEB_2020_PERC
    df["recovery"] = RECOVERY
    df["recovery%"] = RECOVERY_PERC
    df["now as percent of feb 2020"] = NOW_AS_OF_FEB_2020
    df["YTD 2020"] = YTD_2020
    df["YTD 2021"] = YTD_2021
    df["YTD change"] = CHG
    df["YTD change%"] = CHG_PERC
    df["average 2019"] = AVG_2019
    df["average 2020"] = AVG_2020
    df["difference in averages"] = DIFF_AVG
    df["difference in averages%"] = DIFF_AVG_PERC

    return df


def news_release_numbers(fname: str = "data/RIVE$HWS.xlsx", num_top_results: int = 10, current_date : str = None):
    """news_release_numbers calculates all of the numbers we typically use in the IEEP monthly news releases

    Parameters
    ----------
    fname : str, optional
        Path to the EDD data we want to process, by default "data/RIVE$HWS.xlsx"
    num_top_results: int, optional
        Number of top industry gains/losses to display in the output
    current_date: str
        If we want to simulate this back in time, then pass a value for current date in the format Mon-Yr
        Example: Jan-21; Mar-13; Dec-19
        If left as None (default), uses the latest date available
    """
    if pd.options.display.max_rows < num_top_results:
        pd.options.display.max_rows = num_top_results
    # First, load the dataframe
    df_processed = _kleinhenz_process(fname=fname)

    if current_date is not None:
        df_processed = df_processed.loc[:, :current_date]

    # Get the DF for jus tthe 2-digit NAICS Sectors
    twodigit = df_processed[df_processed["Industry Level"] == 2]

    # Now get the easy-to-compute statistics
    unempl = df_processed[df_processed["TITLE"] == "Civilian Unemployment Rate"]

    # Get current and previous month's unemployment unempl, and last year's
    current = (
        unempl.loc[:, :"MTM"].iloc[:, -3].name
    )  # Most recent month wil be right behind MTM based on construction
    prev_month = (
        unempl.loc[:, :"MTM"].iloc[:, -4].name
    )  # Previous month will be right behind
    split_current = current.split("-")
    month, year = split_current[0], split_current[1]
    last_year_colname = f"{month}-{str(int(year) - 1)}"

    # Loop through the DF columns and find the (month, unempl rate) max
    sub = unempl.loc[:, "Jan-19":current]
    maxmonth, maxrate = "", 0
    for mo, rate in sub.iteritems():
        if rate.iloc[0] > maxrate:
            maxrate = rate.iloc[0]
            maxmonth = mo

    UNEMPL_CURRENT = float(unempl[current])
    UNEMPL_PREV = float(unempl[prev_month])
    UNEMPL_LAST_YEAR = float(unempl[last_year_colname])
    MAX_UNEMP = (maxmonth, str(maxrate * 100) + "%")

    # Industry (CES) statistics
    # Additional industries to exclude beyond just the "00-" codes
    EXCLUDED_INDUSTRIES = [
        "Service Providing",
        "Private Service Providing",
        "Total, All Industries",
        "Total Farm",
        "Total Private",
        "Goods Producing",
    ]

    # Clean the TITLE column
    df_processed["TITLE"] = df_processed["TITLE"].str.strip()

    total_nonfarm = df_processed[df_processed["TITLE"] == "Total Nonfarm"]

    TOTAL_NONFARM_CURRENT = float(total_nonfarm[current])
    TOTAL_NONFARM_LAST_MONTH = float(total_nonfarm[prev_month])
    TOTAL_NONFARM_LAST_YEAR = float(total_nonfarm[last_year_colname])
    TOTAL_NONFARM_FEB_2020_PERC = float(total_nonfarm["now minus feb 2020%"])
    TOTAL_NONFARM_CHANGE = TOTAL_NONFARM_CURRENT - TOTAL_NONFARM_LAST_MONTH
    RECOVERY_PERCENTAGE = round(float(total_nonfarm["recovery%"]), 2)

    # Calculate the max drawdown for each industry
    pre_recession_to_present = twodigit.loc[:, "Feb-20":current]
    pre_recession_to_present["Max Drawdown"] = pre_recession_to_present.min(
        axis=1
    ) - pre_recession_to_present.max(axis=1)

    twodigit["Max Drawdown"] = pre_recession_to_present.loc[:, "Max Drawdown"]

    # Sort the dataframe in descending order by the best performing industries MTM
    # Then get rid of aggregates, which all begin their NAICS codes with "00-"
    # Finally, get rid of industries we want to exclude from our summary

    df_sorted = twodigit.sort_values(by="MTM", ascending=False)
    df_sorted = df_sorted[~df_sorted["SS-NAICS"].str.contains("00-")]
    df_sorted = df_sorted[~df_sorted["TITLE"].isin(EXCLUDED_INDUSTRIES)]

    slow_movers = df_sorted.copy()
    slow_movers["Absolute MTM"] = slow_movers["MTM"].apply(np.abs)
    slow_movers.sort_values(by="Absolute MTM", ascending=False)

    NUM_INDUSTRIES_INCREASED = sum(df_sorted["MTM"] > 0)
    NUM_INDUSTRIES_DECREASED = sum(df_sorted["MTM"] < 0)

    TOP_GAINS = df_sorted.head(num_top_results)[["TITLE", "MTM", "Max Drawdown"]]
    TOP_LOSSES = df_sorted.tail(num_top_results)[
        ["TITLE", "MTM", "Max Drawdown"]
    ].sort_values(by="MTM")
    SLOW_MOVERS = slow_movers.tail(num_top_results)[["TITLE", "MTM", "Max Drawdown"]]

    # Print all of the outputs

    print("")
    print("CPS STATISTICS - ALL NOT SEASONALY ADJUSTED")
    print("---------------------------------------")
    print("")

    print(f"UNEMPLOYMENT RATE for {current}: {UNEMPL_CURRENT * 100}%")
    print(f"UNEMPLOYMENT RATE for {prev_month}: {UNEMPL_PREV * 100}%")
    print(f"UNEMPLOYMENT RATE for {last_year_colname}: {UNEMPL_LAST_YEAR * 100}%")
    print(f"MAX UNEMPLOYMENT RATE: {MAX_UNEMP}")

    print("")
    print("CES STATISTICS - ALL NOT SEASONALY ADJUSTED")
    print("---------------------------------------")
    print("")

    print(f"TOTAL NONFARM FOR {current}: {int(TOTAL_NONFARM_CURRENT)}")
    print(f"TOTAL NONFARM FOR {prev_month}: {int(TOTAL_NONFARM_LAST_MONTH)}")
    print(f"TOTAL NONFARM FOR {last_year_colname}: {int(TOTAL_NONFARM_LAST_YEAR)}")
    print(
        f"TOTAL NONFARM AS PERCENT OF FEB 2020: {round(TOTAL_NONFARM_FEB_2020_PERC * 100, 2)}%"
    )
    print(f"CHANGE IN TOTAL NONFARM FROM PREVIOUS MONTH: {int(TOTAL_NONFARM_CHANGE)}")
    print(
        f"TOTAL NONFARM GROWTH RATE OVER THE LAST MONTH: {round((TOTAL_NONFARM_CURRENT/TOTAL_NONFARM_LAST_MONTH - 1) * 100, 2)}%"
    )
    print(f"TOTAL NONFARM RECOVERY SINCE PANDEMIC DROP: {RECOVERY_PERCENTAGE * 100}%")

    print("")

    print(
        f"NUMBER OF INDUSTRIES GAINING EMPLOYMENT MONTH TO MONTH: {NUM_INDUSTRIES_INCREASED}"
    )
    print(
        f"NUMBER OF INDUSTRIES LOSING EMPLOYMENT MONTH TO MONTH: {NUM_INDUSTRIES_DECREASED}"
    )

    print("")
    print(f"TOP {num_top_results} INDUSTRY GAINS: \n {TOP_GAINS}")
    print("")
    print(f"TOP {num_top_results} INDUSTRY LOSSES: \n {TOP_LOSSES}")
    print("")
    print(f"TOP {num_top_results} SMALLEST MOVEMENTS: \n {SLOW_MOVERS}")

    print("")

    return UNEMPL_CURRENT


if __name__ == "__main__":
    res = news_release_numbers(fname="data/RIVE$HWS.xlsx")
