import os
from dotenv import load_dotenv
import pandas
import requests

load_dotenv()

API_KEY = os.getenv("API_KEY_ACS")
STATE = "06"  # California state geoID
PALM_SPRINGS = "55254"
BASE_URL = "https://api.census.gov/data/2019/acs/acs5"


def get_population_estimate(city):
    pop_est = "B01001_001E"  # according to 2019 variable list
    total_population = BASE_URL + f"?get=NAME,{pop_est}&for=place:{city}&in=state:{STATE}"
    try:
        r = requests.get(total_population)
        print(r.json())
        # [['NAME', 'B01001_001E', 'state', 'place'], ['Palm Springs city, California', '47897', '06', '55254']]
    except:
        print(total_population)
        print("Connection refused by the server..")


pop_group = "B01001"


def collect_group(city, group):
    temp = BASE_URL + f"?get=group({group})&for=place:{city}&in=state:{STATE}&key={API_KEY}"
    try:
        r = requests.get(temp)
        print(r.json())
        # [['NAME', 'B01001_001E', 'state', 'place'], ['Palm Springs city, California', '47897', '06', '55254']]
    except:
        print(temp)
        print("Connection refused by the server..")


# get_population_estimate(PALM_SPRINGS)
# https://github.com/datamade/census
collect_group(PALM_SPRINGS, pop_group)

# def generate_csv(group):
#     """
#     This function allows us to pull any series we want and export it to a human-readable (i.e., column names are in English) dataframe + .csv files.

#     Input group: One Series ID from acs  
#     """

#     pass


    
