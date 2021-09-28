import json
import pandas as pd
import us

from bidict import bidict
from typing import Dict

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources

# -------------------------------
# Utility Functions
# -------------------------------

# Functions for generating relevant datasets


def generate_lookup_tables() -> dict:
    # Load datasets
    cbsas = pd.read_csv("datasets/cbsas.csv", skipfooter=4)
    cities = pd.read_csv("datasets/city_geoids.csv")
    decoder_states = {k.fips: k.abbr.lower() for k in us.states.STATES_AND_TERRITORIES}

    # Rename columns to make sure they are standardized

    cities.rename(
        columns={"GEOID": "fips_city", "USPS": "abbr_st", "NAME": "name_city"},
        inplace=True,
    )

    cbsas.rename(
        columns={
            "CBSA Title": "name_msa",
            "CBSA Code": "fips_msa",
            "County/County Equivalent": "name_county",
            "FIPS County Code": "fips_county",
            "State Name": "name_state",
            "FIPS State Code": "fips_state",
        },
        inplace=True,
    )

    # Preprocess data

    # County names are unique UP TO STATE, so we need to get the state name in there
    cbsas["fips_state"] = (
        cbsas["fips_state"].astype(str).str.pad(width=2, side="left", fillchar="0")
    )
    cbsas["abbr_st"] = cbsas["fips_state"].apply(
        lambda x: decoder_states.get(str(x), None)
    )
    cbsas["name_county"] = cbsas["name_county"] + ", " + cbsas["abbr_st"]

    # County codes are unique UP TO STATE, so we need to concatenate them to get unique keys
    cbsas["fips_county"] = (
        cbsas["fips_state"].astype(str) + "_" + cbsas["fips_county"].astype(str)
    )

    cities["name_city"] = (
        cities["name_city"].str.rsplit(" ", 1).str[0]
    )  # Get rid of city type specification
    cities["name_city"] = (
        cities["name_city"].astype(str) + ", " + cities["abbr_st"].astype(str)
    )  # Add state to the city name
    cities.drop_duplicates(subset=["name_city"], inplace=True)  # Drop duplicate cities
    cities["fips_city"] = (
        cities["fips_city"].astype(str).str.pad(width=7, side="left", fillchar="0")
    )

    # Make a separate dataset for MSAs
    msas = cbsas.drop_duplicates(subset=["fips_msa"], keep="first")

    # Generate lookup tables for bidicts
    decoder_cities = dict(zip(cities["fips_city"], cities["name_city"].str.lower()))
    decoder_counties = dict(zip(cbsas["fips_county"], cbsas["name_county"].str.lower()))
    decoder_msas = dict(zip(msas["fips_msa"], msas["name_msa"].str.lower()))

    # Save the dictionaries in JSON format

    with open("lookuptables/cities.json", "w", encoding="utf-8") as f:
        json.dump(decoder_cities, f, ensure_ascii=False, indent=4)

    with open("lookuptables/counties.json", "w", encoding="utf-8") as f:
        json.dump(decoder_counties, f, ensure_ascii=False, indent=4)

    with open("lookuptables/msas.json", "w", encoding="utf-8") as f:
        json.dump(decoder_msas, f, ensure_ascii=False, indent=4)

    with open("lookuptables/states.json", "w", encoding="utf-8") as f:
        json.dump(decoder_states, f, ensure_ascii=False, indent=4)

    return decoder_cities, decoder_counties, decoder_msas, decoder_states


def load_decoder_tables(convert_to_bidict: bool = True):
    # Load the files
    with pkg_resources.open_text("lowe.locations.lookuptables", "cities.json") as f:
        cities = json.load(f)
    with pkg_resources.open_text("lowe.locations.lookuptables", "counties.json") as f:
        counties = json.load(f)
    with pkg_resources.open_text("lowe.locations.lookuptables", "msas.json") as f:
        msas = json.load(f)
    with pkg_resources.open_text("lowe.locations.lookuptables", "states.json") as f:
        states = json.load(f)

    if convert_to_bidict:
        cities = bidict(cities)
        counties = bidict(counties)
        msas = bidict(msas)
        states = bidict(states)

    return cities, counties, msas, states


# -------------------------------
# Conversion Functions
# -------------------------------

# Functions to convert dictionaries from FIPS values to name values and vice versa


def fips2name(loc: Dict[str, str]) -> Dict[str, str]:
    """fips2name converts a dictionary with keys corresponding to geography types ("state", "msa", "county", "city")
    and values being FIPS codes to a dictionary with the same keys but the values being the corresponding names in English

    Parameters
    ----------
    loc : Dict[str, str]
        Location dictionary where the keys are strictly contained in the set {"state", "msa", "county", "city"}
        Values are FIPS codes:
            state: 2-digit code (padded with "0" on the left if < 10: that is, "9" --> "09")
            msa: 5-digit code for MSA
            county: Code for county in the format [statecode]_[countycode]. Can just pass countycode if state is passed as well
            city: 5-digit city code or 7-digit code if state is not passed. Make sure state is left-padded as mentioned above

    Returns
    -------
    Dict[str, str]
        Dictionary with the same keys, but the values correspond to English names
    """
    # Quirks:
    # County FIPS codes are in the format state[2]_county[1-4]
    # City FIPS codes are all unique (they include state codes as first 2 characters)
    # MSA FIPS codes are all unique

    loc_city = loc.get("city", None)
    loc_county = loc.get("county", None)
    loc_msa = loc.get("msa", None)
    loc_state = loc.get("state", None)

    if loc_county is not None:
        if "_" not in loc_county:
            try:
                loc_county = loc_state + "_" + loc_county
            except TypeError:
                print(
                    "ERROR: Make sure to either pass in county FIPS as [state]_[county] or include state as well"
                )

    cities, counties, msas, states = load_decoder_tables()

    res = dict({})

    if loc_city is not None:
        if len(loc_city) < 7:
            loc_city = loc_state + loc_city
        res["city"] = cities[loc_city]
    if loc_county is not None:
        if "_" not in loc_county:
            print(
                "Warning: county FIPS codes should be in the format [statecode]_[countycode]"
            )
        res["county"] = counties[loc_county]
    if loc_msa is not None:
        res["msa"] = msas[loc_msa]
    if loc_state is not None:
        res["state"] = states[loc_state]

    # If only the city is passed in and not the state, infer it

    if res.get("city", None) is not None and res.get("state", None) is None:
        st = res.get("city", None).split(",")[-1]
        res["state"] = st

    return res


def _name2fips_helper(name: str, codetype: str = None) -> Dict[str, str]:
    """_name2fips_helper converts the name of one region to its corresponding FIPS code

    Parameters
    ----------
    name : str
        Name of the region to translate
    codetype : str, optional
        The type of region to pass, by default None
        Example: if I pass in "ca", I should set codetype="state".
        Possible values are "state", "msa", "county", and "city"

    Returns
    -------
    Dict[str, str]
        [description]
    """
    name = name.lower()
    codetype = codetype.lower()
    cities, counties, msas, states = load_decoder_tables()

    if codetype == "state" or codetype == "states":
        return states.inverse[name]
    elif codetype == "msa" or codetype == "msas":
        return msas.inverse[name]
    elif codetype == "county" or codetype == "counties":
        if "_" not in name:
            print("Warning: Pass in county FIPS codes as [state]_[county]")
        return counties.inverse[name]
    elif codetype == "city" or codetype == "cities":
        return cities.inverse[name]

    return None


def name2fips(loc: Dict[str, str]) -> Dict[str, str]:
    """name2fips converts a dictionary with keys corresponding to geography types ("state", "msa", "county", "city").
    Values are english names of locations. Note that the state must be included in each geography.
    It's annoying, but necessary to guarantee uniqueness (msas, counties, and cities in different states can and do have the same name)
    Example:
        loc = {'city': 'palm springs, ca',
            'county': 'riverside county, ca',
            'msa': 'riverside-san bernardino-ontario, ca',
            'state': 'ca'}
        name2fips(loc) -->
            {'city': '0655254', 'county': '06_65', 'msa': '40140', 'state': '06'}

    Parameters
    ----------
    loc : dict
        A dictionary with the same keys, but values corresponding to FIPS codes
    """
    res = dict({})
    for key, value in loc.items():
        res[key] = _name2fips_helper(name=value, codetype=key)
    return res


# -------------------------------
# Search Functions
# -------------------------------

# Utilities to search for FIPS codes based on names
# or search for names based on FIPS codes


def generate_df_json(codetype: str):
    """Generates a dataframe from a decoder JSON file

    Parameters
    ----------
    codetype : str
        Type of file to read. Possible values are "city", "county", "msa", "states"
    """
    cities, counties, msas, states = load_decoder_tables(convert_to_bidict=False)

    if codetype.lower() in ["state", "states"]:
        df = pd.DataFrame.from_dict(states, orient="index", columns=["name"])
        df["fips"] = df.index
        df.reset_index(inplace=True, drop=True)
        return df

    if codetype.lower() in ["msa", "msas"]:
        df = pd.DataFrame.from_dict(msas, orient="index", columns=["name"])
        df["fips"] = df.index
        df.reset_index(inplace=True, drop=True)
        return df

    if codetype.lower() in ["county", "counties"]:
        df = pd.DataFrame.from_dict(counties, orient="index", columns=["name"])
        df["fips"] = df.index
        df.reset_index(inplace=True, drop=True)
        return df

    if codetype.lower() in ["city", "cities"]:
        df = pd.DataFrame.from_dict(cities, orient="index", columns=["name"])
        df["fips"] = df.index
        df.reset_index(inplace=True, drop=True)
        return df

    return None


# TODO: Consolidate both search functions


def search(query: str, codetype: str, search_on: str = "name") -> pd.DataFrame:
    """search searches the relevant dataset specified by codetype for all entries matching the fips code or name provided

    Parameters
    ----------
    query : str
        Search query to run on the dataset
    codetype : str
        Dataset to look into. Possible values are "state", "msa", "county", "city"
    search_on : str, optional
        Search by "fips" or by "name", by default "name"
        If "name", pass in the name of the geography you want to find the FIPS code for

    Returns
    -------
    None. Prints the first 25 search results in dataframe format
    """
    df = generate_df_json(codetype=codetype)
    df = df.astype(str)  # Convert all cols to string
    # df[df['A'].str.contains("hello")]
    df = df[df[search_on].str.contains(query)]
    pd.options.display.max_rows = len(df) if len(df) < 25 else 25
    print(df)
    return None


"""
if __name__ == "__main__":
    PALM_SPRINGS = "55254"
    STATE = "06"
    loc = {"state": "06", "city": "55254", "county": "65", "msa": "40140"}
    english = fips2name(loc)
    # print(name2fips(english))
    search(query="palm", codetype="city", search_on="name")
"""
