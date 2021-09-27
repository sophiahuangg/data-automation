# Lowe Package

This is an importable Python package we have developed with the goal of making automation easier. There are 4 main modules as of now:

- **locations**: Location decoding for FIPS codes. Allows for translation between names and codes -- especially useful for ACS utilities
- **acs**: API wrapper and resources for the American Community Survey
- **fred**: API wrapper and resources for FRED data
- **edd**: Resources for automating EDD analysis for news release data. In the future, this may contain utilities for analyzing our employment data

Since we install this package as an editable module (through `setup.py` in the root directory, which is activated in the setup step `pip install -e .`), you can import these packages within **any** script so long as you are using a conda environment that has it installed.

## lowe.acs
`lowe.acs` contains an asynchronous API wrapper for the American Community Survey API. To use this, you will want to import the `ACSClient` class from `lowe.acs.acs_async`:

```python
from lowe.acs.ACSClient import ACSClient
```

Now, you need to create an `ACSClient` object and initialize its `aiohttp` session:

```python
client = ACSClient() # Make sure your .env file has a variable named API_KEY_ACS
# Else, if varname is the name of your ACS API key in your .env file:
client = ACSClient(key_env_name = "varname")

client.initialize() # Initialize the aiohttp session
```

Now, you can make a request using the `get_acs()` function. The docstring is listed below:

```python
async def get_acs(
    self,
    vars: List[str],
    start_year: Union[int, str],
    end_year: Union[int, str],
    location: Union[Dict[str, str], List[Dict[str, str]]],
    translate_location: bool = False,
    tabletype: Union[str, List[str]] = None,
    infer_type: bool = True,
    varfile: Union[str, List[str]] = None,
    estimate: Union[int, str] = "5",
    join: bool = False,
    debug: bool = False,
):
    """get_acs queries the ACS API and gathers data for any subject or data table into pandas dataframes

    Parameters
    ----------
    vars : List[str]
        List of tables we want to grab from ACS, example ["S1001", "S1501"]
    start_year : Union[int, str]
        Year we want to start collecting data from, earliest being "2011"
    end_year : Union[int, str]
        Last year we want to collect data from, latest being "2019". Must be >= year_start
    location : Union[Dict[str, str], List[Dict[str, str]]]
        Dictionary with the following keys to specify location:
        {
            "state": str, FIPS code of the state,
            "msa": str, code for the MSA,
            "county": str, FIPS code for the county,
            "city": str, FIPS code for the city of interest
        }
        NOTE: You may also pass a list of location dictionaries -- this is the preferred method, since it will parallelize easily
    translate_location: bool
        Whether or not we want to convert the location dictionary to FIPS codes. This essentially does
            location = lowe.locations.lookups.name2fips(location)
        Note that when passing in a dictionary with name vakues instead of FIPS values, all non-state values must have
        the state attached to it. That is, if I want to query for Palm Springs, I would do {city: "palm springs, ca"}
        For safety, always pass strings in as lowercase. Checks are in place for this but they may not be comprehensive
    tabletype : Union[str, List[str]], optional
        Table type to collect, must be one of ["detail", "subject", "dprofile", "cprofile"]
        Respectively, these are Detailed Tables, Subject Tables, Data Profiles, and Comparison Profiles
        If there are various types of tables being collected with one call, pass a list of length len(vars)
        Each entry of this list should correspond to the table type of the corresponding entry in
        NOTE: Pass as None (defualt) if you want to infer the table type
    infer_type: bool, optional
        Whether or not we want to infer table types
    varfile: Union[str, List[str]]
        File (or list of files) that should be used to translate variable names
        NOTE: Pass None (default) if you want to infer the varfile.
    estimate: Union[int,str]
        ACS estimates to gather (1, 3, or 5-year)
    join: bool, optional
        Whether or not to join all the results together into one large table, by default True
    debug: bool, optional
        If True, prints out extra information useful for debugging

    Returns
    -------
    pd.DataFrame, List[pd.DataFrame]
        If only one table is called, then returns the dataframe. Else, return a list of dataframes
    """
    # [Code is here]
```

An example call to the function might look something like

```python

locs = [{"state": str(st.fips)} for st in us.states.STATES]

responses = await client.get_acs(
        vars=subjects,
        start_year="2012",
        end_year="2019",
        location=locs,
        infer_type=True,
        estimate="5",
    )
```

Note that `client.get_acs` is an asynchronous function (coroutine), so you must use the `await` keyword when calling it if you want to return a dataframe or list of dataframes and not a coroutine object.

Putting it all together, we have

```python
import asyncio
from lowe.acs.acs_async import ACSClient

async def main():
    client = ACSClient() # Make sure your .env file has a variable named API_KEY_ACS

    client.initialize() # Initialize the aiohttp session

    locs = [{"state": str(st.fips)} for st in us.states.STATES]

    responses = await client.get_acs(
            vars=subjects,
            start_year="2012",
            end_year="2019",
            location=locs,
            varfile=[
                "tableids/subject_vars_2019.json",
            ],
            infer_type=True,
            estimate="5",
            join=False,
            debug=False,
        )

    await client.close() # Close the aiohttp client session

    # [do any data processing here]
    return final_product

asyncio.run(main())
```

The column names are a bit messy and may take a bit of tweaking to get right for filtering and renaming. For that reason, we recommend developing in a notebook or ipython until you know what you want to do, and then migrating over to a `.py` script afterwards.

## lowe.fred

The FRED API wrapper works very similar to the ACS wrapper. It can be imported by

```python
from lowe.fred.FREDClient import FREDClient

client = FREDClient() # Initialize the FRED Client, assuming your API key is in your .env file as API_KEY_FRED
# Else, you can run
# client = FREDClient(key_env_name = "varname")
# where varname is the name of the variable corresponding to your FRED API key

resp = await client.get_fred(
        vars=subjects, # list of subject IDs to pull (available from their website)
        startDate="2009-01-01",
        endDate="2010-01-01",
        file_type="json", # always pass json here
        frequency="a", # Options are "m", "q", and "a'
        export=False, # Usually want to rename columns first
        debug=True,
    )

await client.close()
```

## lowe.locations

The core of this subpackage is effectively working with **Location Dictionaries**. These are dictionaries where the keys are strictly contained in `{"state", "msa", "county", "city"}`, which are used to specify geographies within the United States. Location dictionaries are heavily used in the ACS API wrapper since this is how we let ACS know what geography we are looking for. Values can either be the actual names (lowercase), or **FIPS (Federal Information Processing Standards)** Codes.

FIPS Codes are unique codes for geographies that allow us to easily search them up if we know their codes. A couple quirks about FIPS codes:
- Pass them in as strings
- FIPS codes are unique up to state -- county and city codes are prefaced by the state code
- City codes are all 7 characters long -- the first two correspond to the state, and the last 5 correspond to the city within the state
- County codes vary in length and are in the format `"[state_code]_[county_code]"`. For the purposes of using the API wrapper, you can omit the first part and just use the county code so long as you specify the state as well.
- MSA codes are unique but will still need to be paired with state in ACS queries.

Location dictionaries with name values are pretty straightforward, with some exceptions:
- pass everything in as lowercase
- counties must have the word `"county"` at the end of the name
- MSA, county, and cities need to have `, st` at the end, where `st` is the abbreviation for the state. So, I could have a location dictionary that looks like:

```python
loc = {
    "state" = "ca",
    "msa" = "riverside-san bernardino-ontario, ca",
    "county" = "riverside county",
    "city" = "rancho mirage"
}
```

How can we translate these names into FIPS codes that we can send to the ACS API? Glad you asked:

There are 3 main utilities in the `lowe.locations` package, all of which are contained in the `lookups.py` file. These utilities are 

- `name2fips(loc: dict)` -- converts a location dictionary with name values to a location dictionary with FIPS code values
- `fips2name(loc: dict)` -- converts a location dictionary with FIPS values to a location dictionary with name values
- `search(query, geography_type, search_on)` -- searches for a specific region of type `geography_type` (either state, MSA, county, or city) based on either the name or the FIPS code, specified by `search_on`. Values for `search_on` can be `"name"` or `"fips"`.

These functions can be imported with

```python
from lowe.locations.lookups import name2fips, fips2name, search
```

There are a **lot** of wrinkles to iron out with this package, so please keep in contact with the managers as development continues and we will add new features and bug fixes as we go.

## lowe.edd

This package contains utilities for automating EDD news release analysis. As we continue, we will add automated employment graphs to this package as well.

## Features to Come

We want to eventually add a `lowe.cli` package that contains command line utilities. An example of a useful function would be an integration of `lowe.locations.lookups.search` so that we can quickly search for FIPS codes of different geographies. This can be done easily through [`Click`](https://click.palletsprojects.com/en/8.0.x/), and will likely be assigned to someone 

```bash
$ search fips city palm

                     name     fips
831            palmer, ak  0258660
2401     desert palms, ca  0619022
2787         la palma, ca  0640256
3085         palmdale, ca  0655156
3086      palm desert, ca  0655184
...                   ...      ...
31603       palmarejo, pr  7257978
31604          palmas, pr  7258365
31605  palmas del mar, pr  7258602
31606      palma sola, pr  7258613
31607          palmer, pr  7258666
```

We also want to add a `lowe.utils` package that includes small utilities that we can use. These don't have to be complicated, just convenient things we may want to use a lot