import aiohttp
import datetime
import json
import os
import pandas as pd
import requests

from dotenv import load_dotenv, find_dotenv
from typing import Union, List


class BLSClient(object):
    def __init__(self, key_env_name: str = "API_KEY_BLS"):
        """the BLS Client class provides methods for wrapping around the BLS client

        Parameters
        ----------
        key_env_name : str, optional
            name of the environment variable in your .env
            file corresponding to your BLS API key, by default "API_KEY_BLS"
        """
        load_dotenv(find_dotenv())
        self.API_KEY = os.environ.get(key_env_name, None)
        try:
            assert self.API_KEY is not None
        except AssertionError:
            print(
                f"Error: make sure you have your BLS API key loaded as an environment variable under the name {key_env_name}."
            )

        self.header = {"Content-type": "application/json"}
        self.BASE_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

    def get_bls(
        self,
        seriesid: Union[str, List[str]],
        startyear: str = "2011",
        endyear: str = "2014",
        annualaverage: bool = False,
        catalog: bool = False,
        calculations: bool = False,
        aspects: bool = False,
    ):
        args = locals()
        payload = {}

        for k, v in args.items():
            if isinstance(v, bool):
                v = str(v).lower()
            if v is not None and k != "self" and v != "false":
                payload[k] = v

        payload["registrationkey"] = self.API_KEY
        data = json.dumps(payload)

        r = requests.post(url=self.BASE_URL, data=data, headers=self.header)
        data_json = json.loads(r.text)

        # Process Result

        assert data_json["status"] == "REQUEST_SUCCEEDED", "Request Failed"

        seriesnames = [s["seriesID"] for s in data_json["Results"]["series"]]

        dfs = []

        for series in seriesnames:
            print(series)
            raw = data_json["Results"]["series"]
            df = pd.json_normalize(raw, record_path="data")
            print(df)

            df["time"] = df["periodName"] + " " + df["year"]
            df["time"] = pd.to_datetime(df["time"])
            df = df.sort_values(by="time", ascending=True)

            df = df.drop(columns = ["footnotes", "period", "periodName"])

            dfs.append(df)

        return dfs


def main():
    client = BLSClient()
    test = client.get_bls(
        ["CUUR0000SA0", "SUUR0000SA0"],
    )
    print(test[0])


if __name__ == "__main__":
    main()
