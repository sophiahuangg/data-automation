import requests
from dotenv import load_dotenv
load_dotenv() 
import os
API_KEY = os.getenv('API_KEY')


state = '06' # California state geoID
PALM_SPRINGS = '55254'
def get_population_estimate(city, year): 
    pop_est = 'B01001_001E' # according to 2019 variable list
    total_population = 'https://api.census.gov/data/{}/acs/acs5?get=NAME,{}&for=place:{}&in=state:{}'.format(year, pop_est, city, state)
    try:
        r = requests.get(total_population)
        print(r.json())
        # [['NAME', 'B01001_001E', 'state', 'place'], ['Palm Springs city, California', '47897', '06', '55254']]
    except:
        print(total_population)
        print("Connection refused by the server..")


get_population_estimate(PALM_SPRINGS, '2019')
