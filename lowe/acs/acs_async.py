import asyncio
import aiohttp
import json
import os
import pandas as pd

from aiolimiter import AsyncLimiter
from dotenv import load_dotenv
from typing import Union, List

# @ext:njpwerner.autodocstring
# https://marcobelo.medium.com/setting-up-python-black-on-visual-studio-code-5318eba4cd00


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
            assert self.key is not None
        except AssertionError:
            print(
                f"Error: please make sure you have your ACS API key loaded as an environment variable under the name {key_env_name}."
            )

    async def initialize(self):
        self.session = await aiohttp.ClientSession()

    async def close(self):
        if not self.session.closed:
            await self.session.close()

    def _base_uri(self, year: Union[int, str], is_subject: bool = True):
        base = f"https://api.census.gov/data/{str(year)}/acs/acs5"
        return base if not is_subject else base + "/subject"

    async def _collect_subject_table(
        self,
        tableid: str,
        year: Union[int, str],
        city_geoid: str,
        state: str = "06",
        is_subject: bool = True,
    ):
        """_collect_subject_table is a helper function that wraps a request to the ACS API

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
        # Check to see if the client session exists
        try:
            assert self.session is not None
        except AssertionError:
            print("Error: Please initialize client session with `client.initialize()`")

        base = self._base_uri(year=year, is_subject=is_subject)

        params = {
            "get": f"group({tableid})",
            "for": f"place:{city_geoid}",
            "in": f"state:{state}",
            "key": self.API_KEY,
        }

        if not is_subject:
            params["get"] = tableid + ","

        async with self.session as sesh:
            resp = await sesh.get(base, params=params)
        return await resp.json()

    async def _process_request(
        self,
        tableid: str,
        year: Union[int, str],
        city_geoid: str,
        state: str = "06",
        is_subject: bool = True,
        varfile: str = "acs_subjects_2019.json",
    ):
        # Pulls data from ACS
        resp = await self._collect_subject_table(
            tableid=tableid,
            year=year,
            city_geoid=city_geoid,
            state=state,
            is_subject=is_subject,
        )
        # Opens the JSON file with subject tables info
        with open(varfile) as f:
            subjectDict = json.load(f)

        # ids: list of subject ids
        # vals: list of corresponding values
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
