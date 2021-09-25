# Lowe Package

This is an importable Python package we have developed with the goal of making automation easier. There are 4 main modules as of now:

- **locations**: Location decoding for FIPS codes. Allows for translation between names and codes -- especially useful for ACS utilities
- **acs**: API wrapper and resources for the American Community Survey
- **fred**: API wrapper and resources for FRED data
- **edd**: Resources for automating EDD analysis for news release data. In the future, this may contain utilities for analyzing our employment data

Since we install this package as an editable module (through `setup.py` in the root directory, which is activated in the setup step `pip install -e .`), you can import these packages within **any** script so long as you are using a conda environment that has it installed.

## lowe.acs
`lowe.acs` contains an asynchronous API wrapper for the American Community Survey API.

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

## Features to Come

We want to eventually add a `lowe.cli` package that contains command line utilities. An example of a useful function would be an integration of `lowe.locations.lookups.search` so that we can quickly search for FIPS codes of different geographies. This can be done quite easily through [`Click`](https://click.palletsprojects.com/en/8.0.x/), and will likely be assigned to someone 

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