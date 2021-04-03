import requests
from dotenv import load_dotenv
load_dotenv() 
import os
API_KEY = os.getenv('API_KEY')
# GET "ACS DEMOGRAPHIC AND HOUSING ESTIMATES"
#get = NAME, S0101_C01_001E & for = place: * & key = YOUR_KEY_GOES_HERE
def get_population_data(city, year): 
    base_url = "https://www.api.census.gov/data/{}/acs/acs5/subject?get=".format(year)
    r = requests.get()
