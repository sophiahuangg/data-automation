from dotenv.main import find_dotenv
import requests
import json
import pandas as pd
import asyncio
import aiohttp
import backoff
import os

from dotenv import load_dotenv, find_dotenv
from typing import Union, List, Dict
from aiolimiter import AsyncLimiter

class FREDClient(object):
    def __init__(self, key_env_name: str = "API_KEY_FRED"):
        """the FRED Client class provides methods for wrapping around the FRED client

        Parameters
        ----------
        key_env_name : str, optional
            name of the environment variable in your .env
            file corresponding to your FRED API key, by default "FRED_KEY_FRED"
        """
        load_dotenv()
        self.API_KEY = os.environ.get(key_env_name, None)
        self.limiter = AsyncLimiter(120, 60)
        try:
            assert self.API_KEY is not None
        except AssertionError:
            print(
                f"Error: make sure you have your FRED API key loaded \
                    as an environment variable under the name {key_env_name}."
            )

    async def initialize(self):
        self.session = aiohttp.ClientSession()

    async def close(self):
        if not self.session.closed:
            await self.session.close()

    def _base_url(self):
        base = "https://api.stlouisfed.org/fred/series/observations"
        return base

    @backoff.on_exception(
        backoff.expo, (aiohttp.ClientError, aiohttp.ClientResponseError), max_tries=3
    )    
    async def _scrape_fred_json(
        self,
        seriesid,
        startDate="2009-01-01",
        endDate="2010-12-01",
        file_type="json",
        frequency="m",
    ):
        try:
            assert self.session is not None
        except AssertionError:
            print(
                "Error: Please initialize client \
                   session with `client.initialize()`"
            )

        base_url = self._base_url()
        api_key = self.API_KEY

        params = {
            "series_id": seriesid,
            "observation_start": startDate,
            "observation_end": endDate,
            "frequency": frequency,
            "api_key": api_key,
            "file_type": file_type
        }

        async with self.session.get(base_url, params = params) as resp:
            return await resp.json()


    # test = scrape_fred_json("CPIAUCSL")


    def _parse_fred_series(self, series):
        observation_date = []
        value = []

        for item in series:
            val = item["value"]
            value.append(val)
            time = item["date"]
            observation_date.append(time)

        df = pd.DataFrame({"observation_date": observation_date, "value": value})
        return df


    async def _full_fred_scrape(
        self, seriesid, startDate, endDate, file_type, frequency, export=False
    ):
        result = []
        req = await self._scrape_fred_json(seriesid, startDate, endDate, file_type, frequency)
        seriesid1 = seriesid
        try:
            series = req["observations"]
        except KeyError:
            print(
                f"Error: make sure you check the conditions for the value of frequency\n {req}."
            )
        #print("series = ", series)

        df = self._parse_fred_series(series)
        result.append([seriesid1, df])

        if export:
            for res in result:
                name = res[0] + ".csv"
                res[1].to_csv(name, index=False)
        
        # print(export)

        return result

    async def get_FRED(
        self,
        vars: List[str],
        startDate: str,
        endDate: str,
        file_type: str,
        frequency: str,
        export: bool,
    ):
        """get_FRED queries the FRED API and gathers data for any subject or data table into pandas dataframes

        Parameters
        ----------
        vars : List[str]
            List of tables we want to grab from FRED, example ["GNPCA", "GDP"]
        startDate : str
            The first date we want to collect data at
        endDate : str
            The last date we want to collect data at. Must be >= startDate
        file_type: str
            The file type you want to return. File types must be in xml, json, txt, xls
        frequency: str
            The frequency of the data you want to grab: m (monthly), a (annual), q (quarterly), etc
        export: bool
            Allows you to decide whether you want to export the file as a csv
        """
        async with self.limiter:
            resp = await asyncio.gather(
                *[
                    self._full_fred_scrape(
                        seriesid=table, 
                        startDate=startDate, 
                        endDate=endDate, 
                        file_type=file_type, 
                        frequency=frequency, 
                        export=export
                        ) 
                    for table in vars
                ]
            )
        
        return resp
    

    # test = full_fred_scrape(
    #     "CPIAUCSL",
    #     startDate="2009-01-01",
    #     endDate="2010-12-01",
    #     file_type="json",
    #     api_key="c40f3024dd6d518feaf4fc4cbb9ff3fa",
    #     frequency="m",
    #     export=True,
    # )

async def main():
    subjects = ["GNPCA", "GDP"]

    client = FREDClient()
    await client.initialize()


    test_resp = await client.get_FRED(
        vars=subjects,
        startDate="2009-01-01",
        endDate="2010-01-01",
        file_type="json",
        frequency="a",
        export=False,
    )

    await client.close()

    print(test_resp)
    return test_resp



asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())
