import os
from dotenv import load_dotenv
import pandas as pd
import requests
import json

load_dotenv()

API_KEY = os.getenv("API_KEY_ACS")
STATE = "06"  # California state geoID
PALM_SPRINGS = "55254"

# TODO: write docstrings
# TODO: create a function for getting data for different years

def base_url(YEAR):
    """
    Helper function. Returns the base URL for the ACS API for a year
    """
    if type(YEAR) != str:
        print("R U SRS")
    return f"https://api.census.gov/data/{str(YEAR)}/acs/acs5"

def get_population_estimate(city, year):
    """
    
    Input: city, year: string
    
    """
    pop_est = "B01001_001E"  # according to 2019 variable list
    total_population = base_url(year) + f"?get=NAME,{pop_est}&for=place:{city}&in=state:{STATE}"
    try:
        r = requests.get(total_population)
        print(r.json())
        # [['NAME', 'B01001_001E', 'state', 'place'], ['Palm Springs city, California', '47897', '06', '55254']]
    except:
        print(total_population)
        print("Connection refused by the server..")


pop_group = "B01001"


def collect_group(city, group, year):
    """
    Pulls the data from ACS with the series id from the group for city and year

    Input: city, group, year: string

    """
    temp = base_url(year) + f"?get=group({group})&for=place:{city}&in=state:{STATE}&key={API_KEY}"
    try:
        r = requests.get(temp)
        # print(r.json())
        return r.json()
        # [['NAME', 'B01001_001E', 'state', 'place'], ['Palm Springs city, California', '47897', '06', '55254']]
    except:
        print(temp)
        print("Connection refused by the server..")


# get_population_estimate(PALM_SPRINGS)
# https://github.com/datamade/census
collect_group(PALM_SPRINGS, pop_group, "2019")

def year_df(group, year, city = PALM_SPRINGS):
    """
    This function allows us to pull any series we want and export it to a human-readable (i.e., column names are in English) dataframe for one year.

    We want series IDs that only end in 'E'
    Input group: One Series ID from acs  
    """
    with open("acs_vars_2019.json") as vars_json:
        varDict = json.load(vars_json)


    # Format of LoL: list of lists, 
    #   list 0 = list of series ids
    #   list 1 = list of corresponding values
    LoL =  collect_group(city, group, year) # Pulls the data from ACS

    ids = LoL[0]
    vals = LoL[1]
    
    concept_label = []
    values = []
    
    for i in range(len(ids)):
        if (ids[i]) == 'NAME':
            break
        if (ids[i][-1]) == 'E':
            # RENAME THE SERIES HERE
            ser = ids[i]
            concept_label.append(varDict[ser]["Concept"] + " " + varDict[ser]["Label"])
            values.append(vals[i])
            
    
    acs_df = pd.DataFrame({
        "concept_label" : concept_label,
        "values" : values
    })

    acs_df["year"] = year
    acs_df = acs_df.pivot(index = "year", columns = "concept_label", values = "values")
    
    return acs_df

def generate_csv(group, start_year = '2011', end_year = '2019', city = PALM_SPRINGS):
    """
    """
    
    dfs = []

    for year in range(int(start_year), int(end_year) + 1):
        dfs.append(year_df(group, str(year), city))
    
    result = pd.concat(dfs)
    return result
    
#print(generate_csv(pop_group, start_year="2011", end_year="2019", city=PALM_SPRINGS))

print(cg.address(city = "Palm Springs", state = "CA"))