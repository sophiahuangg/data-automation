import pytest
from lowe.acs.ACSClient import ACSClient
from lowe.locations.lookup import search, name2fips, fips2name

def test_add():
    assert 1+1 == 2

@pytest.mark.asyncio
async def test_overall():
    client = ACSClient()
    await client.initialize()
    fip_code = search('cathedral city, ca', codetype="city", search_on="name").iloc[0][1]

    loc1 = {
    "state": "06",
    "city": "14260"
    }

    loc2 = {"city": "0636434"}

    locs = [loc1, loc2] 

    raw_resp = await client.get_acs(vars = ['S1701'],
                     start_year='2018',
                     end_year='2018',
                     location=locs,
                     estimate="5")
    print(raw_resp)
    assert False



