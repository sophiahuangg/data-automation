`python3 -m pytest tests/test_lowe/test_acs/test_acsclient.py`

## Description of Test

- Check 3 tables with 1 and 5 years (6 tables)
- For each table check 3 different values
- Total of 3 tables * 2 estimate years * 3 different entries

Common Tables Used in Lowe
- S0801
- S2801
- S1901
- S1501
- DP05

Compare client pull with manual check eg. at https://data.census.gov/cedsci/table?q=coachella,%20ca%20S1501 

# Dev Notes and Questions
- No 1 year estimation for the tables and cities lowe uses