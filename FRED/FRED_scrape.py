import requests
import json
import pandas as pd

def scrape_fred_json(seriesid, startDate = "2009-01-01", endDate = "2010-12-01", file_type = "json", api_key = "c40f3024dd6d518feaf4fc4cbb9ff3fa", frequency = "m"):
    base_url = "https://api.stlouisfed.org/fred/series/observations?"
    observation_start =  startDate
    observation_end = endDate

    combined_url = base_url + "series_id=" + seriesid + "&observation_start=" + observation_start + \
    "&observation_end=" + observation_end + "&frequency=" + frequency + "&api_key=" + api_key + "&file_type=" + file_type
    p = requests.get(combined_url)
    json_data = json.loads(p.text)

    return json_data

# test = scrape_fred_json("CPIAUCSL")

def parse_fred_series(series):
    observation_date = []
    value = []

    for item in series:
        val = item['value']
        value.append(val)
        time = item['date']
        observation_date.append(time)
    
    df = pd.DataFrame({"observation_date": observation_date, "value": value})
    return df

def full_fred_scrape(seriesid, startDate, endDate, file_type, api_key, frequency, export = False):
    result = []
    req = scrape_fred_json(seriesid, startDate, endDate, file_type, api_key, frequency)
    seriesid1 = seriesid
    series = req["observations"]

    df = parse_fred_series(series)
    result.append([seriesid1, df])

    if export:
        for res in result:
            name = res[0] + ".csv"
            res[1].to_csv(name, index = False)
    
    return result

test = full_fred_scrape("CPIAUCSL", startDate = "2009-01-01", endDate = "2010-12-01", file_type = "json", api_key = "c40f3024dd6d518feaf4fc4cbb9ff3fa", frequency = "m", export = True)
