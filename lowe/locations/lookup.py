from bidict import bidict
import json
import pandas as pd
import us


def generate_lookup_tables() -> dict:
    # Load datasets
    cbsas = pd.read_csv("datasets/cbsas.csv", skipfooter=4)
    cities = pd.read_csv("datasets/city_geoids.csv")
    decoder_states = {k.fips: k.abbr.lower() for k in us.states.STATES}

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
    cbsas["name_msa"] = cbsas.name_msa.str.rsplit(" ", 1).str[
        0
    ]  # Remove the state from the msa name column
    cbsas["name_msa"] = cbsas["name_msa"].str[:-1]  # Remove comma at the end

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

def fips2name(code: str, codetype: str) -> str:
    """fips2name converts a FIPS code to 

    Parameters
    ----------
    code : str
        [description]
    codetype : str
        [description]

    Returns
    -------
    str
        [description]
    """
    # Quirks:
    # County FIPS codes are in the format state[2]_county[1-4]
    # City FIPS codes are in the format 

    codetype = codetype.lower()
    cities, counties, msas, states = load_decoder_tables()

    if codetype == "state" or codetype == "states":
        return states[code]
    elif codetype == "msa" or codetype == "msas":
        return msas[code]
    elif codetype == "county" or codetype == "counties":
        return counties[code]
    elif codetype == "city" or codetype == "cities":
        return cities[code]

    return None

def name2fips(loc: dict) -> str:
    """[summary]

    Parameters
    ----------
    loc : dict
        [description]

    Returns
    -------
    str
        [description]
    """
    cities, counties, msas, states = load_decoder_tables()]

    pass
    


if __name__ == "__main__":
    load_decoder_tables()
