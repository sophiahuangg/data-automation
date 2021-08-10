import asyncio
import aiohttp
import json
import os
import pandas as pd

from aiolimiter import AsyncLimiter
from dotenv import load_dotenv
from typing import Union, List

load_dotenv()

API_KEY = os.environ.get("API_KEY_ACS", None)
STATE = "06"  # California state geoID
PALM_SPRINGS = "55254"
RANCHO_MIRAGE = "59500"
pop_group = "B01001"
pop_subj = "S0101"

geoids = pd.read_csv("geoids_clean.csv")

def _base_uri_subject(year: Union[str, int]):
    """Create a base URL for a subject table API call"""
    return f"https://api.census.gov/data/{year}/acs/acs5/subject"

async def _collect_subject_table(session : aiohttp.ClientSession, subject: str, year: str, city_geoid : str, state : str = "06", api_key : str = API_KEY):
    uri = _base_uri_subject(year=year)

    params = {
        "get" : f"group({subject})",
        "for" : f"place:{city_geoid}",
        "in" : f"state:{state}",
        "key": api_key
    }

    async with session.get(uri, params=params) as r:
        resp = await r.json()

    return {year : resp}