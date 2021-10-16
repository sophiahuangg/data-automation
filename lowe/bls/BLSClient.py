import aiohttp
import os

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
                f"Error: make sure you have your ACS API key loaded as an environment variable under the name {key_env_name}."
            )
        
        self.headers = {'Content-type': 'application/json'}
        self.BASE_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

    def get_bls(series: Union[str, List[str]]):
        pass
