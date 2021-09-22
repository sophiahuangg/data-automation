from bidict import bidict
import json
import pandas as pd
from typing import Dict
import us


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


def load_decoder_tables() -> dict:
    # Load the files
    with open("lookuptables/cities.json", "r", encoding="utf-8") as f:
        cities = json.load(f)
    with open("lookuptables/counties.json", "r", encoding="utf-8") as f:
        counties = json.load(f)
    with open("lookuptables/msas.json", "r", encoding="utf-8") as f:
        msas = json.load(f)
    with open("lookuptables/states.json", "r", encoding="utf-8") as f:
        states = json.load(f)

    cities = bidict(cities)
    counties = bidict(counties)
    msas = bidict(msas)
    states = bidict(states)

    return cities, counties, msas, states


# TODO: Insert function to clean / pad county codes appropriately


def fips2name(loc: Dict[str, str]) -> Dict[str, str]:
    """fips2name converts a location dict to a dict of names

    Parameters
    ----------
    loc : dict
        [description]

    Returns
    -------
    Dict[str, str]
        [description]
    """
    # Quirks:
    # County FIPS codes are in the format state[2]_county[1-4]
    # City FIPS codes are all unique
    # MSA FIPS codes are all unique

    loc_city = loc.get("city", None)
    loc_county = loc.get("county", None)
    loc_msa = loc.get("msa", None)
    loc_state = loc.get("state", None)

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
    """[summary]

    Parameters
    ----------
    name : str
        [description]
    codetype : str, optional
        [description], by default None

    Returns
    -------
    Dict[str, str]
        [description]
    """
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
    """[summary]

    Parameters
    ----------
    loc : dict
        [description]
    """
    res = dict({})
    for key, value in loc.items():
        res[key] = _name2fips_helper(name=value, codetype=key)
    return res


if __name__ == "__main__":
    PALM_SPRINGS = "55254"
    STATE = "06"
    loc = {"state": "06", "city": "55254", "county": "65", "msa": "40140"}
    english = fips2name(loc)
