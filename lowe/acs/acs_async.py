import asyncio
import aiohttp
import backoff
import json
import os
import pandas as pd
import us

from bidict import bidict
from dotenv import load_dotenv, find_dotenv
from typing import Union, List, Dict

# @ext:njpwerner.autodocstring
# https://marcobelo.medium.com/setting-up-python-black-on-visual-studio-code-5318eba4cd00

# State -- first two digits of city geoid (state=*)
# MSA - geocomp (MSA code, state)
# County -- where to find the codes???? (county, state)
# Place (city) -- (geoid,state) "place="

# TODO: Implement location encoding within responses (both FIPS and English)
# Revisit after implementing lowe.locations


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
        # TODO: Add functionality for other kinds of estimates (non 5-year)
        # 1 year: acsse
        # 3 year: acs3

        surveys = {"1": "acsse", "3": "acs3", "5": "acs5"}

        tabletypes = {
            "detail": "", # Default table type
            "subject": "/subject",
            "profile": "/profile",
            "data profile": "/profile",
            "dprofile": "/profile",
            "comparison profile": "/cprofile",
            "comp profile": "/cprofile",
            "cprofile": "/cprofile"
        }

        survey = surveys[int(estimate)]
        try:
            table = tabletypes[tabletype.lower()]
        except KeyError:
            print("ERROR: Please provide valid table type")

        base = f"https://api.census.gov/data/{str(year)}/acs/{survey}"
        
        return base + table

    @backoff.on_exception(
        backoff.expo, (aiohttp.ClientError, aiohttp.ClientResponseError), max_tries=1
    )
    async def _collect_subject_table(
        self,
        tableid: str,
        year: Union[int, str],
        location: Dict[str, str],
        is_subject: bool = True,
        debug: bool = False,
    ):
        # TODO: Add functionality to lookup state codes from 2-character
        # state codes (i.e. CA <--> 06). This needs to be a new module
        # TODO: Check that the process works for non-subject tables as well
        # Check to see if the client session exists
        try:
            assert self.session is not None
        except AssertionError:
            print(
                "Error: Please initialize client \
                   session with `client.initialize()`"
            )

        base = self._base_uri(year=year, is_subject=is_subject)

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

        if not is_subject:
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
        is_subject: bool = True,
        varfile: str = "acs_subjects_2019.json",
        debug: bool = False,
    ):
        print(year)
        # Pulls data from ACS
        if debug:
            print("making request...")
        resp = await self._collect_subject_table(
            tableid=tableid,
            year=year,
            location=location,
            is_subject=is_subject,
        )

        if debug:
            print("opening JSON...")
        # Opens the JSON file with subject tables info

        with open(varfile) as f:
            subjectDict = json.load(f)

        # ids: list of subject ids
        # vals: list of corresponding values
        if debug:
            print("post-processing....")
        ids, vals = resp[0], resp[1]
        concept_label = []
        values = []

        state_decoding = bidict({k.fips: k.abbr for k in us.states.STATES})

        for idx, id in enumerate(ids):
            subject = id
            # Search for the subject ids in our JSON file
            # try/catch so we only query query-able fields in the JSON
            try:
                concept_label.append(
                    subjectDict[subject]["concept"]
                    + " "
                    + subjectDict[subject]["label"]
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

        acs_subject_pivoted["state"] = state_decoding[location["state"]]

        return acs_subject_pivoted

    async def _subject_tables_range(
        self,
        tableid: str,
        location: Dict[str, str],
        start_year: Union[int, str] = "2011",
        end_year: Union[int, str] = "2019",
        is_subject: bool = True,
        debug: bool = False,
    ):
        """Helper function to get multiple years of ACS data for a single subject and return them as a single dataframe"""
        year_range = range(int(start_year), int(end_year) + 1)
        results = await asyncio.gather(
            *[
                self._process_request(
                    tableid=tableid,
                    year=year,
                    location=location,
                    is_subject=is_subject,
                    debug=debug,
                )
                for year in year_range
            ]
        )

        res = pd.concat(results)
        # TODO: Figure out if we want to sort this dataframe or not -- depends on size (determine from testing)

        return res

    async def get_acs(
        self,
        vars: List[str],
        start_year: Union[int, str],
        end_year: Union[int, str],
        location: Dict[str, str],
        is_subject: Union[bool, List[bool]] = True,
        join: bool = True,
        debug: bool = True,
    ):
        """get_acs queries the ACS API and gathers data for any subject or data table into pandas dataframes

        Parameters
        ----------
        vars : List[str]
            List of tables we want to grab from ACS, example ["S1001", "S1501"]
        year_start : Union[int, str]
            Year we want to start collecting data from, earliest being "2011"
        year_end : Union[int, str]
            Last year we want to collect data from, latest being "2019". Must be >= year_start
        location : Dict[str, str]
            Dictionary with the following keys to specify location:
            {
                "state": str, FIPS code of the state,
                "msa": str, code for the MSA,
                "county": str, FIPS code for the county,
                "
            }
        is_subject : Union[bool, List[bool]], optional
            boolean value indiciating whether the tables are specified are subject tables or not, by default True
            If some are subject tables and some are not, you can pass a list of length len(vars) indicating whether or not each table is a subject table
        join: bool, optional
            Whether or not to join all the results together into one large table, by default True
        """
        # Split the vars into equal partitions
        if isinstance(is_subject, bool):
            dfs = await asyncio.gather(
                *[
                    self._subject_tables_range(
                        tableid=table,
                        start_year=start_year,
                        end_year=end_year,
                        location=location,
                        is_subject=is_subject,
                        debug=debug,
                    )
                    for table in vars
                ]
            )
        elif isinstance(is_subject, list):
            dfs = await asyncio.gather(
                *[
                    self._subject_tables_range(
                        tableid=table,
                        start_year=start_year,
                        end_year=end_year,
                        location=location,
                        is_subject=is_subject[i],
                        debug=debug,
                    )
                    for i, table in enumerate(vars)
                ]
            )

        if join:
            # Iterate through the dfs and join them together on 'year'
            base = dfs[0]
            for df in dfs[1:]:
                intermediate = base.join(df, how="left", on="year")
            return intermediate

        else:
            return dfs


async def main():
    subjects = ["S1001", "S1501"]
    PALM_SPRINGS = "55254"
    # RANCHO_MIRAGE = "59500"
    STATE = "06"

    client = ACSClient()
    await client.initialize()

    # loc = {"state": STATE, "city": PALM_SPRINGS}
    loc = {"state": STATE}

    test_resp = await client.get_acs(
        vars=subjects,
        start_year="2011",
        end_year="2019",
        location=loc,
        is_subject=True,
        join=False,
        debug=True,
    )

    await client.close()

    print(test_resp[1]["state"])

    return test_resp


asyncio.run(main())
