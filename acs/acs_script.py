import os
from dotenv import load_dotenv
import pandas
import requests

load_dotenv()

API_KEY = os.getenv("API_KEY_ACS")
STATE = "06"  # California state geoID
PALM_SPRINGS = "55254"
BASE_URL = "https://api.census.gov/data/2019/acs/acs5"

# TODO: write docstrings
# TODO: create a function for getting data for different years

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
        return r.json()
        # [['NAME', 'B01001_001E', 'state', 'place'], ['Palm Springs city, California', '47897', '06', '55254']]
    except:
        print(temp)
        print("Connection refused by the server..")


# get_population_estimate(PALM_SPRINGS)
# https://github.com/datamade/census
collect_group(PALM_SPRINGS, pop_group)

def generate_csv(group):
    """
    This function allows us to pull any series we want and export it to a human-readable (i.e., column names are in English) dataframe + .csv files.

    We want series IDs that only end in 'E'
    Input group: One Series ID from acs  
    """


    LoL =  collect_group(PALM_SPRINGS, group)

    seriesId = {}
    
    for i in range(len(LoL[0])):
        if (LoL[0][i][-1]) == 'E':
            seriesId[LoL[0][i]] = LoL[1][i]
    
    print(seriesId)

    
generate_csv(pop_group)
