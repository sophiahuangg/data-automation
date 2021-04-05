import requests
from dotenv import load_dotenv
load_dotenv() 
import os
API_KEY = os.getenv('API_KEY')
STATE = '06' # California state geoID
PALM_SPRINGS = '55254'
BASE_URL = 'https://api.census.gov/data/2019/acs/acs5'

def get_population_estimate(city): 
    pop_est = 'B01001_001E' # according to 2019 variable list
    total_population = BASE_URL + '?get=NAME,{}&for=place:{}&in=state:{}'.format(pop_est, city, STATE)
    try:
        r = requests.get(total_population)
        print(r.json())
        # [['NAME', 'B01001_001E', 'state', 'place'], ['Palm Springs city, California', '47897', '06', '55254']]
    except:
        print(total_population)
        print("Connection refused by the server..")


def aggregate_age_groups(city):
    male_under_5 = 'B01001'
    temp = BASE_URL + '?get=NAME,{}&for=place:{}&in=state:{}&key={}'.format(male_under_5, city, STATE, API_KEY)
    try:
        r = requests.get(temp)
        print(r.html())
        # [['NAME', 'B01001_001E', 'state', 'place'], ['Palm Springs city, California', '47897', '06', '55254']]
    except:
        print(temp)
        print("Connection refused by the server..")

#get_population_estimate(PALM_SPRINGS)

aggregate_age_groups(PALM_SPRINGS)
