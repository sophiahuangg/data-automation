import os
from dotenv import load_dotenv
import pandas as pd
import requests
import json

load_dotenv()

API_KEY = os.getenv("API_KEY_ACS")
STATE = "06"  # California state geoID
PALM_SPRINGS = "55254"
RANCHO_MIRAGE = "59500"
pop_group = "B01001"

geoids = pd.read_csv("geoids_clean.csv")

# ---------------------------
# THINGS TO DO:
# ---------------------------

# MUST-DO:
# TODO: fix docstrings
# TODO: Add function comments 

def geoid_from_city(city):
    """
    Gets the geoid from the city name using the city geocode csv

    Arguments:
        city: (str) city 
            NOTE: must be in the format "Palm Springs, CA"
    """
    # TODO: fix docstring output 

    temp = geoids[geoids["City"] == city] # Filter out all cities that are not targets
    
    geoid = list(temp["city_geoid"])[0] # Grab the first result of the corresponding geoID

    return geoid


def city_from_geoid(geoid):
    """
    Returns the city associated with a particular geoid.
    
    Arguemnts:
        geoid: (str) city geoid (without the state id) ex. "59500"
    """
    # TODO: fix docstring output 

    temp = geoids[geoids["city_geoid"] == int(geoid)] #Filter out all the geoids that are not tarfers
    city = list(temp["City"])[0] #Grab the first result of the corresponding City
    
    return city

def base_url(YEAR):
    """
    Helper function. Returns the base URL for the ACS API for a year
    
    Argument:
        year: (str) year in string format ex. "2021"
    """
    # TODO: fix docstring output 

    if type(YEAR) != str:
        print("R U SRS")
    return f"https://api.census.gov/data/{str(YEAR)}/acs/acs5"

def get_population_estimate(city, year):
    """
    Pulls the population estimate data from ACS for a city and year
    
    Arguements: 
        city: (str) city id in string format ex. "59500"
        year: (str) year in string format ex. "2021"
    
    """
     # TODO: fix docstring output 
    pop_est = "B01001_001E"  # according to 2019 variable list
    total_population = base_url(year) + f"?get=NAME,{pop_est}&for=place:{city}&in=state:{STATE}"
    try:
        r = requests.get(total_population)
        print(r.json())
        # [['NAME', 'B01001_001E', 'state', 'place'], ['Palm Springs city, California', '47897', '06', '55254']]
    except:
        print(total_population)
        print("Connection refused by the server..")


def collect_group(city, group, year):
    """
    Pulls the data from ACS with the series id from the group for city and year

    Arguments:
        city: (str) city id in string format ex. "59500" is Rancho Mirage, CA
        group: (str) Series ID of group you want to pull from format ex. "B01001" is SEX BY AGE
        year: (str) year in string format ex. "2021"
        
    Output:
        List of lists with the series ID in the first list and the value in the second list
        
        Format of LoL: list of lists, 
        list 0 = list of series ids 
            NOTE: at the end of the list "NAME, 'state', 'place'"
        list 1 = list of corresponding values 
            NOTE: at the end of the list ex.'Palm Springs city, California',  '06', '55254'

        ex. # [['B01001_001E', 'NAME', 'state', 'place'], ['47897', 'Palm Springs city, California',  '06', '55254']]
    """
    temp = base_url(year) + f"?get=group({group})&for=place:{city}&in=state:{STATE}&key={API_KEY}"
    try:
        r = requests.get(temp)
        return r.json()
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

    Arguments: 
        group: (str) Series ID of group you want to pull from format ex. "B01001" is SEX BY AGE
        year: (str) year in string format ex. "2021"
        city: (str) city id in string format ex. "59500" is Rancho Mirage, CA
    """
    # TODO: FIX DOCSTRING output

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

def generate_df_city(group, start_year = '2011', end_year = '2019', city = PALM_SPRINGS):
    """
    Generates a dataframe for a city's data from ACS, given a start and end year.

    Arguments:
        
        group: (str) SeriesID group to pull format ex. "B01001" for SEX BY AGE
        year: (str) year in string format ex. "2021"
        start_year: (str) Year to begin collecting data from (must be 2011 or later)
        end_year: (str) Year to stop collecting data from (must be 2019 or less)
        city: (str) city id in string format ex. "59500"
    
    Outputs a dataframe with the following columns: year (index), city (str), and a separate column for each subgroup
    """
    
    dfs = []

    cityName = city_from_geoid(city)

    for year in range(int(start_year), int(end_year) + 1):
        df = year_df(group, str(year), city)
        dfs.append(year_df(group, str(year), city))
    
    result = pd.concat(dfs)

    result["City"] = cityName

    return result

def generate_csv(group, start_year = '2011', end_year = '2019', cities = [PALM_SPRINGS], filename = None):
    """
    Uses generate_df_city to create one large dataframe that encompasses all data for a particular ACS series.

    Inputs:
        group: (str) series ID ex. "B01001" for SEX BY AGE
        start_year: (str) Year to begin collecting data from (must be 2011 or later) ex. "2011"
        end_year: (str) Year to stop collecting data from (must be 2019 or less) ex. "2019"
        cities: (list) List of strings of geo IDs for cities you want to pull ex. ["55254", "59500"]
            for Palm Springs, CA and Rancho Mirage, CA
        filename: (str) Filename to name the output .csv file. Leave as None if you don't want to save a file. ex. "my_acs_data.csv"

    Outputs a datafame with the same format as generate_df_city, but contains multiple levels for the City variable rather than just one.
    """
    dfs = []

    for city in cities:
        df = generate_df_city(group, start_year, end_year, str(city))
        dfs.append(df)

    res = pd.concat(dfs)

    if filename != None:
        res.to_csv(filename, index = True)

    return res

# print(generate_csv(pop_group, start_year="2011", end_year="2019", cities=[PALM_SPRINGS, RANCHO_MIRAGE], filename = "testSet.csv"))
