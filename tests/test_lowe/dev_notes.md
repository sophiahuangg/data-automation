
Test API Wrapper (initalize client, pull data from different soruces (eg. ACS tables) and ensure data equals what is expected. Pick random cells of table and compare between manual access via website vs wrapper). 

eg.: https://data.census.gov/cedsci/table?q=S1901%20Coachella%20Valley 
vs 
```
raw_resp = await client.get_acs(vars = 'S1901',
                     start_year=2019,
                     end_year=2019,
                     location='06065',
                     estimate="5") 
```

test command
`pytest lowe/test/test_acesclient.py`

---

each table has:

5 year estimates, try 3 tables (diff year for each table), for each of table check 3 different values.

and repeat for 1 year
