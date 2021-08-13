import asyncio
import aiohttp
import json
import os
import pandas as pd

from aiolimiter import AsyncLimiter
from dotenv import load_dotenv
from typing import Union, List, Dict

# @ext:njpwerner.autodocstring
# https://marcobelo.medium.com/setting-up-python-black-on-visual-studio-code-5318eba4cd00

# State -- first two digits of city geoid (state=*)
# MSA - geocomp (MSA code, state)
# County -- where to find the codes???? (county, state)
# Place (city) -- (geoid,state) "place="

# TODO: Implement backoff for retries


class ACSClient(object):
    def __init__(self, key_env_name: str = "API_KEY_ACS"):
        """the ACS Client class provides methods for wrapping around the ACS client

        Parameters
        ----------
        key_env_name : str, optional
            name of the environment variable in your .env file corresponding to your ACS API key, by default "API_KEY_ACS"
        """
        load_dotenv()
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

    def _base_uri(self, year: Union[int, str], is_subject: bool = True):
        # TODO: Add functionality for other kinds of estimates (non 5-year)
        base = f"https://api.census.gov/data/{str(year)}/acs/acs5"
        return base if not is_subject else base + "/subject"

    async def _collect_subject_table(
        self,
        tableid: str,
        year: Union[int, str],
        location: Dict[str, str],
        is_subject: bool = True,
        debug: bool = False,
    ):
        """_collect_subject_table is a helper function that wraps a GET request to the ACS API

        Parameters
        ----------
        tableid : str
            [description]
        year : Union[int, str]
            [description]
        city_geoid : str
            [description]
        state : str, optional
            [description], by default "06"
        is_subject : bool, optional
            [description], by default True

        Returns
        -------
        [type]
            [description]
        """
        # TODO: Add functionality to lookup state codes from 2-character state codes (i.e. CA <--> 06)
        # TODO: Check that the process works for non-subject tables as well
        # Check to see if the client session exists
        try:
            assert self.session is not None
        except AssertionError:
            print("Error: Please initialize client session with `client.initialize()`")

        base = self._base_uri(year=year, is_subject=is_subject)

        state = location.pop("state")

        key_translations = {"msa": "geocomp", "city": "place", "county": "county"}

        # The 'for' part is a little more tricky. We need to append MSA, county, and city in that order, with %20 in between
        place = ""
        for k, v in location.items():
            if v is not None:
                place += (
                    f"%20{key_translations[k]}:{v}"
                    if len(place) > 0
                    else f"{key_translations[k]}:{v}"
                )

        params = {
            "get": f"group({tableid})",
            "for": place,
            "in": f"state:{state}",
            "key": self.API_KEY,
        }

        if not is_subject:
            params["get"] = tableid + ","

        async with self.session as sesh:
            resp = await sesh.get(base, params=params, raise_for_status=True)
            if debug:
                print(resp.url)
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
        # Pulls data from ACS
        print("making request...")
        resp = await self._collect_subject_table(
            tableid=tableid,
            year=year,
            location=location,
            is_subject=is_subject,
        )

        if debug:
            print(resp.url)
        # Opens the JSON file with subject tables info
        print("opening JSON...")
        with open(varfile) as f:
            subjectDict = json.load(f)

        # ids: list of subject ids
        # vals: list of corresponding values
        print("post-processing....")
        ids, vals = resp[0], resp[1]
        concept_label = []
        values = []

        for idx, id in enumerate(ids):
            subject = id
            # Search for the subject ids in our JSON file
            # try/catch so we only query query-able fields in the JSON
            try:
                concept_label.append(
                    subjectDict[subject][
                        "concept" + " " + subjectDict[subject]["label"]
                    ]
                )
                values.append(vals[idx])
            except KeyError:
                continue

        # Intermediate output DF
        subject_df = pd.DataFrame(
            {"concept_label": concept_label, "values": values, "year": year}
        )

        # Final DF that can be merged
        acs_subject_pivoted = subject_df.pivot(
            index="year", columns="concept_label", values="values"
        )

        return acs_subject_pivoted

    async def _subject_tables_range(
        self,
        tableid: str,
        city_geoid: str,
        start_year: Union[int, str] = "2011",
        end_year: Union[int, str] = "2019",
        state: str = "06",
        is_subject: bool = True,
    ):
        """Helper function to get multiple years of ACS data for a single subject and return them as a single dataframe"""
        year_range = range(int(start_year), int(end_year) + 1)
        results = await asyncio.gather(
            *[
                self._process_request(
                    tableid=tableid,
                    year=year,
                    city_geoid=city_geoid,
                    state=state,
                    is_subject=is_subject,
                )
                for year in year_range
            ]
        )

        res = pd.concat(results)
        # TODO: Figure out if we want to sort this dataframe or not -- depends on size (determine from testing)

        return res

    async def get_acs(
        vars: List[str],
        year_start: str,
        year_end: str,
        city_geoid: Union[int, str],
        state: str,
        is_subject: bool = True,
    ):
        # Split the vars into equal partitions
        pass


async def main():
    pop_subj = "S0101"
    PALM_SPRINGS = "55254"
    RANCHO_MIRAGE = "59500"
    STATE = "06"

    client = ACSClient()
    await client.initialize()

    loc = {"state": STATE, "city": PALM_SPRINGS}

    test_resp = await client._collect_subject_table(
        tableid=pop_subj, year="2019", location=loc, debug=True
    )

    print(test_resp)

    await client.close()

    return test_resp


asyncio.run(main())
