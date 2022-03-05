import pytest
from lowe.acs.ACSClient import ACSClient
from lowe.locations.lookup import search, name2fips, fips2name

@pytest.mark.asyncio
class TestSearch_and_Get:
    """
    tests:
    - ACSClient Initialization
    - client.get_acs()

    needs working:
    - lowe.locations.lookup search()
    """

    async def test_add(self):
        assert 1+1 == 2

    async def test_5year_s2801_1(self):
        client = ACSClient()
        await client.initialize()
        fip_code = search('cathedral city, ca', codetype="city", search_on="name").iloc[0][1]

        # fip_code2 = search('coachella, ca', codetype="city", search_on="name").iloc[0][1]

        locs = [{'city': fip_code}]
        
        resp = await client.get_acs(vars = ['S2801'],
                        start_year='2019',
                        end_year='2019',
                        location=locs,
                        estimate="5")
        col_name = "TYPES OF COMPUTERS AND INTERNET SUBSCRIPTIONS Estimate Percent Total households TYPE OF INTERNET SUBSCRIPTIONS With an Internet subscription: Broadband of any type"
        col_sub = [col_name, 'state', 'city']
        if len(resp[col_sub]) != 1:
            assert False

        value = float(resp[col_sub][col_name].iloc[0])

        assert value == 82.2

    async def test_5year_s2801_2(self):
        client = ACSClient()
        await client.initialize()
        fip_code = search('cathedral city, ca', codetype="city", search_on="name").iloc[0][1]

        # fip_code2 = search('coachella, ca', codetype="city", search_on="name").iloc[0][1]

        locs = [{'city': fip_code}]
        
        resp = await client.get_acs(vars = ['S2801'],
                        start_year='2019',
                        end_year='2019',
                        location=locs,
                        estimate="5")
        col_name = "TYPES OF COMPUTERS AND INTERNET SUBSCRIPTIONS Estimate Percent Total households TYPES OF COMPUTER Has one or more types of computing devices: Desktop or laptop"
        col_sub = [col_name, 'state', 'city']
        if len(resp[col_sub]) != 1:
            assert False

        value = float(resp[col_sub][col_name].iloc[0])

        assert value == 75.3

    async def test_5year_s2801_3(self):
        client = ACSClient()
        await client.initialize()
        # fip_code = search('cathedral city, ca', codetype="city", search_on="name").iloc[0][1]

        fip_code2 = search('coachella, ca', codetype="city", search_on="name").iloc[0][1]

        locs = [{'city': fip_code2}]
        
        resp = await client.get_acs(vars = ['S2801'],
                        start_year='2019',
                        end_year='2019',
                        location=locs,
                        estimate="5")
        col_name = "TYPES OF COMPUTERS AND INTERNET SUBSCRIPTIONS Estimate Total Total households TYPE OF INTERNET SUBSCRIPTIONS With an Internet subscription: Broadband of any type"
        col_sub = [col_name, 'state', 'city']
        if len(resp[col_sub]) != 1:
            assert False

        value = float(resp[col_sub][col_name].iloc[0])

        assert value == 11273
