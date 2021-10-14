import asyncio
import aiohttp
import backoff
import json
import os
import pandas as pd
import requests

from dotenv import load_dotenv, find_dotenv
from lowe.locations.lookup import name2fips, fips2name
from typing import Union, List, Dict

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources

from . import tableids


class ACSClient(object):
    def __init__(self, key_env_name: str = "API_KEY_ACS"):
        """the ACS Client class provides methods for wrapping around the ACS client

        Parameters
        ----------
        key_env_name : str, optional
            name of the environment variable in your .env
            file corresponding to your ACS API key, by default "API_KEY_ACS"
        """
        load_dotenv(find_dotenv())
        self.API_KEY = os.environ.get(key_env_name, None)
        try:
            assert self.API_KEY is not None
        except AssertionError:
            print(
                f"Error: make sure you have your ACS API key loaded as an environment variable under the name {key_env_name}."
            )

        self.surveys = {"1": "acs1", "3": "acs3", "5": "acs5"}

        self.tabletypes = {
            "detail": "",  # Default table type
            "subject": "/subject",
            "profile": "/profile",
            "data profile": "/profile",
            "dprofile": "/profile",
            "comparison profile": "/cprofile",
            "comp profile": "/cprofile",
            "cprofile": "/cprofile",
        }

    async def initialize(self):
        self.session = aiohttp.ClientSession()

    async def close(self):
        if not self.session.closed:
            await self.session.close()

    def _base_uri(
        self,
        year: Union[int, str],
        tabletype: str = "detail",
        estimate: Union[int, str] = "5",
    ):
        """_base_uri generates the base URI for the ACS API for each type of table and the 1, 3, and 5 year estimate tables

        Parameters
        ----------
        year : Union[int, str]
            Year we want to pull the data for
        tabletype : str, optional
            Type of table we want to pull, by default "detail"
            Options are:
            - "detail" <--> ACS Detail tables,
            - "subject" <--> Subject Tables,
            - ["profile", "data profile", or "dprofile"] <--> Data Profile Tables,
            - ["comparison profile", "comp profile", "cprofile"] for ACS comparison profiles
        estimate : Union[int,str], optional
            [description], by default "5"

        NOTE: 1 year estimate URLs will almost definitely not work, but 3- and 5-year estimates will

        Returns
        -------
        str
            Base URL for querying ACS API
        """
        survey = self.surveys[str(estimate)]
        try:
            table = self.tabletypes[tabletype.lower()]
        except KeyError:
            print("ERROR: Please provide valid table type")

        base = f"https://api.census.gov/data/{str(year)}/acs/{survey}"

        return base + table

    def _get_var_defs(
        self,
        fname: str,
        year: Union[int, str] = "2019",
        tabletype: str = "detail",
        estimate: Union[int, str] = "5",
    ):
        """Checks to see if the variable decoding JSON is included in the tableids/ folder, and if not, downloads it"""
        # First, get the base url
        base = self._base_uri(
            year=str(year), tabletype=tabletype, estimate=str(estimate)
        )
        req_uri = base + "/variables.json"
        vars = requests.get(req_uri)
        js = vars.json()

        with open(fname, "w", encoding="utf-8") as f:
            json.dump(js, f, ensure_ascii=False, indent=4)

        return js

    def _infer_table_type(self, tableid: str):
        tableid = tableid.lower()
        if tableid[0] == "b":
            return "detail"
        elif tableid[0] == "s":
            return "subject"
        elif tableid[0:2] == "dp":
            return "dprofile"
        elif tableid[0:2] == "cp":
            return "cprofile"
        return None

    def _infer_varfile(self, year: Union[int, str], tabletype: str):
        if tabletype.lower() == "detail":
            return f"detail_vars_{str(year)}.json"
        elif tabletype.lower() == "subject":
            return f"subject_vars_{str(year)}.json"
        elif tabletype.lower() == "dprofile":
            return f"dprofile_vars_{str(year)}.json"

    @backoff.on_exception(
        backoff.expo, (aiohttp.ClientError, aiohttp.ClientResponseError), max_tries=5
    )
    async def _collect_table(
        self,
        tableid: str,
        year: Union[int, str],
        location: Dict[str, str],
        tabletype: str = "detail",
        estimate: Union[int, str] = "5",
        debug: bool = False,
    ):
        # Check to see if the client session exists
        try:
            assert self.session is not None
        except AssertionError:
            print(
                "Error: Please initialize client \
                   session with `client.initialize()`"
            )

        base = self._base_uri(year=year, tabletype=tabletype, estimate=estimate)

        key_translations = {"msa": "geocomp", "city": "place", "county": "county"}

        # The 'for' part is a little more tricky. We need to append
        # MSA, county, and city in that order, with %20 in between
        place = ""
        for k, v in location.items():
            if v is not None and k.lower() != "state":
                place += (
                    f"%20{key_translations[k]}:{v}"
                    if len(place) > 0
                    else f"{key_translations[k]}:{v}"
                )

        keyz = list(location.keys())

        if len(keyz) == 1 and "state" in keyz:
            params = {
                "get": f"group({tableid})",
                "for": f"state:{location['state']}",
                "key": self.API_KEY,
            }
        else:
            params = {
                "get": f"group({tableid})",
                "for": place,
                "in": f"state:{location['state']}",
                "key": self.API_KEY,
            }

        if tabletype == "detail" or tabletype == "":
            params["get"] = tableid + ","

        async with self.session.get(base, params=params, raise_for_status=True) as resp:
            if debug:
                print(resp.url)
                print(resp.status)
            return await resp.json()

    async def _process_request(
        self,
        tableid: str,
        year: Union[int, str],
        location: Dict[str, str],
        tabletype: str = "detail",
        estimate: Union[int, str] = "5",
        varfile: str = "subject_vars_2019.json",
        debug: bool = False,
    ):
        # Pulls data from ACS
        if debug:
            print("making request...")
        resp = await self._collect_table(
            tableid=tableid,
            year=year,
            location=location,
            tabletype=tabletype,
            estimate=estimate,
            debug=debug,
        )

        if debug:
            print("opening JSON...")
        # Opens the JSON file with subject tables info

        with pkg_resources.open_text(tableids, varfile) as f:
            subjectDict = json.load(f)

        # ids: list of subject ids
        # vals: list of corresponding values
        if debug:
            print("post-processing....")
        ids, vals = resp[0], resp[1]
        concept_label = []
        values = []

        # state_decoding = bidict({k.fips: k.abbr for k in us.states.STATES})
        location_names = fips2name(location)

        subjectDict = subjectDict["variables"]

        for idx, id in enumerate(ids):
            subject = id
            # Search for the subject ids in our JSON file
            # try/catch so we only query query-able fields in the JSON
            try:
                concept_label.append(
                    (
                        subjectDict[subject]["concept"]
                        + " "
                        + subjectDict[subject]["label"]
                    ).replace("!!", " ")
                )
                values.append(vals[idx])
            except KeyError:
                continue

        # Intermediate output DF
        subject_df = pd.DataFrame(
            {"concept_label": concept_label, "values": values, "year": year}
        )

        # Drop duplicates
        subject_df.drop_duplicates(inplace=True, subset=["concept_label"])

        # Final DF that can be merged
        acs_subject_pivoted = subject_df.pivot(
            index="year", columns="concept_label", values="values"
        )

        acs_subject_pivoted.drop(acs_subject_pivoted.columns[0], axis=1, inplace=True)

        location_str = ""

        for key, value in location_names.items():
            if key.lower() != "state":
                value = value.split(",")[0]
            acs_subject_pivoted[key.lower()] = value.lower()
            location_str += (
                value.lower() if len(location_str) == 0 else " " + value.lower()
            )

        acs_subject_pivoted["location_key"] = location_str

        return acs_subject_pivoted

    async def _tables_range(
        self,
        tableid: str,
        location: Dict[str, str],
        start_year: Union[int, str] = "2015",
        end_year: Union[int, str] = "2019",
        tabletype: str = "detail",
        varfile: str = "subject_vars_2019.json",
        estimate: Union[int, str] = "5",
        debug: bool = False,
    ):
        """Helper function to get multiple years of ACS data for a single subject and return them as a single dataframe"""
        year_range = range(int(start_year), int(end_year) + 1)

        if isinstance(location, dict):  # If there is only one location passed
            # Clean location
            if "city" in location.keys():
                if len(location["city"]) == 7:
                    if "state" not in location.keys():
                        location["state"] = location["city"][
                            0:2
                        ]  # Add the state code to the state key
                    location["city"] = location["city"][2:]  # shave off the state code
            if "county" in location.keys():  # Clean the county
                if "_" in location["county"]:
                    splt = location["county"].split("_")
                    location["county"] = splt[-1]
                    if "state" not in location.keys():
                        location["state"] = splt[0]

            results = await asyncio.gather(
                *[
                    self._process_request(
                        tableid=tableid,
                        year=year,
                        location=location,
                        tabletype=tabletype,
                        estimate=estimate,
                        varfile=varfile,
                        debug=debug,
                    )
                    for year in year_range
                ]
            )
        elif isinstance(location, list):  # If there is more than one location passed in
            for loc in location:
                if "city" in loc.keys():
                    if len(loc["city"]) == 7:
                        if "state" not in loc.keys():
                            loc["state"] = loc["city"][
                                0:2
                            ]  # Add the state code to the state key
                        loc["city"] = loc["city"][2:]  # shave off the state code
                if "county" in loc.keys():  # Clean the county
                    if "_" in loc["county"]:
                        splt = loc["county"].split("_")
                        loc["county"] = splt[-1]
                        if "state" not in loc.keys():
                            loc["state"] = splt[0]

            results = await asyncio.gather(
                *[
                    self._process_request(
                        tableid=tableid,
                        year=year,
                        location=loc,
                        tabletype=tabletype,
                        estimate=estimate,
                        varfile=varfile,
                        debug=debug,
                    )
                    for year in year_range
                    for loc in location
                ]
            )

        res = pd.concat(results)

        return res

    async def get_acs(
        self,
        vars: List[str],
        start_year: Union[int, str],
        end_year: Union[int, str],
        location: Union[Dict[str, str], List[Dict[str, str]]],
        translate_location: bool = False,
        tabletype: Union[str, List[str]] = None,
        infer_type: bool = True,
        varfile: Union[str, List[str]] = None,
        estimate: Union[int, str] = "5",
        join: bool = False,
        debug: bool = False,
    ):
        """get_acs queries the ACS API and gathers data for any subject or data table into pandas dataframes

        Parameters
        ----------
        vars : List[str]
            List of tables we want to grab from ACS, example ["S1001", "S1501"]
        start_year : Union[int, str]
            Year we want to start collecting data from, earliest being "2011"
        end_year : Union[int, str]
            Last year we want to collect data from, latest being "2019". Must be >= year_start
        location : Union[Dict[str, str], List[Dict[str, str]]]
            Dictionary with the following keys to specify location:
            {
                "state": str, FIPS code of the state,
                "msa": str, code for the MSA,
                "county": str, FIPS code for the county,
                "city": str, FIPS code for the city of interest
            }
            NOTE: You may also pass a list of location dictionaries -- this is the preferred method, since it will parallelize easily
        translate_location: bool
            Whether or not we want to convert the location dictionary to FIPS codes. This essentially does
                location = lowe.locations.lookups.name2fips(location)
            Note that when passing in a dictionary with name vakues instead of FIPS values, all non-state values must have
            the state attached to it. That is, if I want to query for Palm Springs, I would do {city: "palm springs, ca"}
            For safety, always pass strings in as lowercase. Checks are in place for this but they may not be comprehensive
        tabletype : Union[str, List[str]], optional
            Table type to collect, must be one of ["detail", "subject", "dprofile", "cprofile"]
            Respectively, these are Detailed Tables, Subject Tables, Data Profiles, and Comparison Profiles
            If there are various types of tables being collected with one call, pass a list of length len(vars)
            Each entry of this list should correspond to the table type of the corresponding entry in
            NOTE: Pass as None if you want to infer the table type
        infer_type: bool, optional
            Whether or not we want to infer table types
        varfile: Union[str, List[str]]
            File (or list of files) that should be used to translate variable names
            NOTE: Pass None (default) if you want to infer the varfile.
        estimate: Union[int,str]
            ACS estimates to gather (1, 3, or 5-year)
        join: bool, optional
            Whether or not to join all the results together into one large table, by default True
        debug: bool, optional
            If True, prints out extra information useful for debugging

        Returns
        -------
        pd.DataFrame, List[pd.DataFrame]
            If only one table is called, then returns the dataframe. Else, return a list of dataframes
        """
        # Split the vars into equal partitions
        if infer_type:
            tabletypes = [self._infer_table_type(var) for var in vars]
            if debug:
                print(tabletypes)

        # Translate the dictionary to FIPS values if necessary
        if translate_location:
            location = name2fips(location)

        if varfile is None:  # We want to infer which file to use
            varfile = [
                self._infer_varfile(
                    tabletype=tabletype, year="2019"
                )  # NOTE: This may not work in later years
                for tabletype in tabletypes
            ]
            varfile = varfile[0] if len(varfile) == 1 else varfile

        if isinstance(varfile, str):
            dfs = await asyncio.gather(
                *[
                    self._tables_range(
                        tableid=table,
                        start_year=start_year,
                        end_year=end_year,
                        location=location,
                        tabletype=tabletypes[0],
                        estimate=estimate,
                        varfile=varfile,
                        debug=debug,
                    )
                    for table in vars
                ]
            )
        elif isinstance(varfile, list):
            dfs = await asyncio.gather(
                *[
                    self._tables_range(
                        tableid=table,
                        start_year=start_year,
                        end_year=end_year,
                        location=location,
                        tabletype=tabletypes[i],
                        varfile=varfile[i],
                        estimate=estimate,
                        debug=debug,
                    )
                    for i, table in enumerate(vars)
                ]
            )

        if join:
            # Iterate through the dfs and join them together on 'year'
            base = dfs[0]
            for df in dfs[1:]:
                intermediate = base.join(df, how="left", on=["year", "state"])
            return intermediate

        else:
            return dfs[0] if len(dfs) == 1 else dfs


"""
async def main():
    subjects = ["S1701"]
    # dp = "DP05"
    # PALM_SPRINGS = "55254"
    # RANCHO_MIRAGE = "59500"
    # STATE = "06"

    client = ACSClient()
    await client.initialize()

    locs = [{"state": str(st.fips)} for st in us.states.STATES]

    # locs = [{"state": "06"}, {"state": "04"}]

    responses = await client.get_acs(
        vars=subjects,
        start_year="2019",
        end_year="2019",
        location=locs,
        infer_type=True,
        estimate="5",
        join=False,
        debug=False,
    )

    responses = responses[
        [
            "state",
            "POVERTY STATUS IN THE PAST 12 MONTHS Estimate Percent below poverty level Population for whom poverty status is determined",
        ]
    ]
    responses = responses.rename(
        columns={
            "POVERTY STATUS IN THE PAST 12 MONTHS Estimate Percent below poverty level Population for whom poverty status is determined": "perc_poverty"
        }
    )

    # final.to_csv("outputs/povertyrates_1year.csv")

    await client.close()

    return responses


asyncio.run(main())
"""
