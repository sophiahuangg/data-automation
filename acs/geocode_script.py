import csv
import pandas as pd

# """
# Script that cleans the geocode csv file to split the city geoid and the state geoid
# And makes it to a new csv file.
# """

geoids = pd.read_csv("city_geoids.csv")

state_geo = []
city_geo = []

for entry in geoids["GEOID"]:
    city = str(entry)[-5:]
    state = str(entry)[:-5]

    state_geo.append(state)
    city_geo.append(city)


geoids["city_geoid"] = city_geo
geoids["state_geoid"] = state_geo

city_name = []

for city in geoids["NAME"]:
    split = city.split(" ")

    split = split[:-1]

    name = ""

    for word in split:
        if split[-1] == word:
            name += word
        else:
            name += word + " "
    
    city_name.append(name)    

geoids["city_name"] = city_name

geoids["combo"] = geoids["city_name"] + ", " + geoids["USPS"]

geoids_clean = pd.DataFrame({
    "City" : list(geoids["combo"]),
    "city_geoid" : list(geoids["city_geoid"]),
    "state_geoid" : list(geoids["state_geoid"])
})

geoids_clean.to_csv("geoids_clean.csv")