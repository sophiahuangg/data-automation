import datetime
import glob
import os
import pandas as pd
import requests

from bidict import bidict
from bs4 import BeautifulSoup


def get_dof_pop_data(path_to_save: str = "scraped-data/"):
    base_url = "https://www.dof.ca.gov/Forecasting/Demographics/Estimates/"
    r = requests.get(base_url, verify=False)
    resp = r.text
    soup = BeautifulSoup(resp, features="html.parser")

    elems = soup.select('a[href*="E-4"], a[href*="e-4"]')
    hrefs = [base_url + elem.get("href") for elem in elems]
    print(hrefs)
    for url in hrefs:
        # Get the link for the Excel file
        r = requests.get(url, verify=False)
        soup = BeautifulSoup(r.text, features="html.parser")
        link_additions = soup.select('a[href$=".xlsx"], a[href$=".xls"]')
        url += link_additions[0].get("href")

        # Generate the output filename from the URL
        url_split = url.lower().split("/")

        path_to_save = path_to_save[:-1] if path_to_save[-1] == "/" else path_to_save

        fname = f"{url_split[url_split.index('e-4') + 1]}_population.xlsx"
        fname = fname.replace("-", "_")

        fname_split = fname.split("_")
        fname_split[1] = (
            fname_split[0][:2] + fname_split[1]
            if len(fname_split[1]) == 2
            else fname_split[1]
        )
        fname = f'{path_to_save}/{"_".join(fname_split)}'

        # Get the Excel file
        xl = requests.get(url, verify=False)

        with open(fname, "wb") as f:
            f.write(xl.content)


def _find_filenames(dir: str = "scraped-data/"):
    """Helper to find the filenames of sheets to analyze.

    Parameters
    ----------
    dir: str
        Directory where the scraped DOF spreadsheets are stored

    """
    # Get the relevant filenames for all excel files
    os.chdir(dir)
    try:
        xls = [filename for filename in glob.glob("*.xls*")]
    finally:
        os.chdir("../")

    files_to_read = []
    start_year = []

    for filename in xls:
        splt = filename.split("_")
        if int(splt[0]) < 1990:
            pass
        else:
            files_to_read.append(filename)
            start_year.append(int(splt[0]))

    idxs = bidict(enumerate(start_year))
    start_year.sort()
    idxs_sorted = bidict(enumerate(start_year))

    filenames_sorted = []

    for i in range(len(idxs_sorted)):
        val = idxs_sorted[i]
        orig_idx = idxs.inverse[val]
        filenames_sorted.append(files_to_read[orig_idx])

    return filenames_sorted


def _clean_colnames(df: pd.DataFrame):
    """Helper function to clean datetime column names and drop non-January entries"""
    renamed = [list(df.columns)[0]]
    for i, col in enumerate(list(df.columns[1:])):
        strcol = str(col).split(" ")[0]
        try:
            dt = datetime.datetime.strptime(strcol, "%Y-%m-%d")
        except ValueError:
            dt = datetime.datetime.strptime(strcol, "%m/%d/%Y")

        if dt.month == 4:
            df = df.drop(col, axis=1)
        else:
            newname = dt.strftime(format="%Y")
            renamed.append(newname)
    df.columns = renamed
    return df


def _county_data_clean_and_join(dir: str = "scraped-data/"):
    """Clean and consolidate the county-level data for 1990-Present"""
    # NOTE: This function will need to be adjusted as more spreadsheets are added by DOF
    fnames = _find_filenames(dir)
    fnames = [dir + fname for fname in fnames]

    # Data for 1990-2000
    county_90s = pd.read_excel(
        fnames[0],
        sheet_name="Table 1CountyState Pop Est",
        skiprows=2,
    ).dropna(how="all")

    county_90s["County"] = county_90s["County"].str.strip().astype(str)

    # Data for 2001-2010
    county_00s = (
        pd.read_excel(
            fnames[1],
            sheet_name="Table 1 County State",
            skiprows=3,
        )
        .dropna(how="all")
        .rename(columns={"COUNTY": "County"})
    )
    county_00s["County"] = county_00s["County"].str.strip().astype(str)

    # Data for 2011-Present

    county_10s = (
        pd.read_excel(fnames[2], sheet_name="Table 1 County State", skiprows=1)
        .dropna(how="all")
        .rename(columns={"COUNTY": "County"}),
    )
    county_10s["County"] = county_10s["County"].str.strip().astype(str)

    final = county_90s.merge(county_00s, on="County").merge(county_10s, on="County")

    final = _clean_colnames(final)
    final = final.rename(
        columns={"County": "Year", "State Total": "California"}
    )  # Useful after transpose
    final = final.set_index("Year", drop=True)

    return final.T


def _city_data_clean_and_join(dir: str = "scraped-data/"):
    """Clean and consolidate the city-level data for 1990-Present"""
    fnames = _find_filenames(dir)
    fnames = [dir + fname for fname in fnames]

    # Data for 1990-2000
    state_90s = pd.read_excel(
        fnames[0],
        sheet_name="Table 2  City Pop Est",
        skiprows=3,
        skipfooter=1,
        na_values=["*"],
    ).dropna(how="all")

    # Clean the column names and values; filter empty rows
    state_90s["City"] = state_90s["City"].str.strip().astype(str)
    state_90s = _clean_colnames(state_90s)
    lastcol = list(state_90s.columns)[-1]
    state_90s = state_90s[~state_90s[lastcol].isna()]

    # Get rid of county totals
    state_90s = state_90s[
        ~state_90s["City"].str.strip().str.contains("Balance Of County")
    ]
    state_90s = state_90s.reset_index(drop=True)

    # Data for 2001-2010
    state_00s = (
        pd.read_excel(
            fnames[1],
            sheet_name="Table 2 City County",
            skiprows=3,
            skipfooter=1,
            na_values=["*"],
        )
        .dropna(how="all")
        .rename(columns={"COUNTY/CITY": "City"})
    )

    # Clean the column names and values; filter empty rows
    state_00s["City"] = state_00s["City"].str.strip().astype(str)
    state_00s = _clean_colnames(state_00s)
    lastcol = list(state_00s.columns)[-1]
    state_00s = state_00s[~state_00s[lastcol].isna()]

    # Get rid of county totals
    state_00s = state_00s[
        ~state_00s["City"]
        .str.strip()
        .str.contains("Balance Of County|Incorporated|County Total")
    ]
    state_00s = state_00s.reset_index(drop=True)

    # Data for 2011-Present
    state_10s = (
        pd.read_excel(
            fnames[2],
            sheet_name="Table 2 City County",
            skiprows=1,
            skipfooter=1,
            na_values=["*"],
        )
        .dropna(axis=0, how="all")
        .dropna(axis=1, how="all")
        .rename(columns={"COUNTY/CITY": "City"})
    )

    # Clean the column names and values; filter empty rows
    state_10s["City"] = state_10s["City"].str.strip().astype(str)
    state_10s = _clean_colnames(state_10s)
    lastcol = list(state_10s.columns)[-1]
    state_10s = state_10s[~state_10s[lastcol].isna()]

    # Get rid of county totals
    state_10s = state_10s[
        ~state_10s["City"]
        .str.strip()
        .str.contains("Balance Of County|Incorporated|County Total")
    ]
    state_10s = state_10s.reset_index(drop=True)

    # Join the results together into one dataframe

    final = state_90s.merge(state_00s, on="City").merge(state_10s, on="City")
    final = final.rename(
        columns={"City": "Year", "State Total": "California"}
    )  # Useful after transpose
    final = final.set_index("Year", drop=True)

    return final.T


def main():
    test = _city_data_clean_and_join(dir="scraped-data/")
    print(test)


if __name__ == "__main__":
    main()
