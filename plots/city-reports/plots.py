import asyncio
import datetime
import os
import time

from functools import wraps

from demographics import (
    city_population_cv_present,
    city_population_cv_time_series,
    pop_growth_rates,
    pop_growth_rates_year_groups,
    age_distribution,
    race_group_distribution,
    households_with_internet,
    # residence_and_work_loc,
)

from income import (
    total_household_income,
    median_household_income,
    household_income_by_class,
)

from employment import (
    avg_monthly_employment,
    employment_composition_pandemic_now,
    unemployment_rates,
    # change_employment_composition, NOT USING
    # employment_composition, NOT USING
    peak_to_trough_empl,
    # change_empl_share_prev_peak_per_sector, NOT USING
)

from taxable_sales import (
    real_nominal_sales_pc_time_series,
    taxable_sales_per_capita_quarters_cv,
    timer,
)

from education_human_capital import human_capital_index_cv, educational_attainment_cv

from health_insurance import health_insurance

from lowe.acs.ACSClient import ACSClient


# ------------------------------
# Helper Functions
# ------------------------------


def _make_dirs(cities: list = None):
    if cities is None:
        cities = [
            "Coachella",
            "Cathedral City",
            "Desert Hot Springs",
            "Indian Wells",
            "Indio",
            "La Quinta",
            "Palm Desert",
            "Palm Springs",
            "Rancho Mirage",
        ]

    for city in cities:
        if not os.path.exists(f"outputs/{city}"):
            os.makedirs(f"outputs/{city}")


def timer_async(f):
    """Decorator that times the amount of time it takes an asynchronous function to
    complete and prints it to standard output"""

    @wraps(f)
    async def wrapper(*args, **kwargs):
        t0 = time.time()
        res = await f(*args, **kwargs)
        tf = time.time()
        print(f"Time for function {f.__name__} to run: {tf - t0:.1f} seconds.")
        return res

    return wrapper


# ------------------------------
# Image Generation Functions
# ------------------------------


@timer_async
async def demographics_plots(
    target_city: str, dof_year: int, acs_year: int, client: ACSClient
):
    # Figure 1
    city_population_cv_present(
        year=dof_year,
        target_city=target_city,
        save_path=f"outputs/{target_city}/City Population, {target_city}, Rest of Coachella Valley, {dof_year}",
    )

    # Figure 2
    city_population_cv_time_series(
        save_path=f"outputs/{target_city}/City Population, Coachella Valley, 1990-{dof_year}"
    )

    # Figure 3
    pop_growth_rates(
        target_city=target_city,
        save_path=f"outputs/{target_city}/Population Growth Rates, {target_city}, Rest of Coachella Valley, 1990-{dof_year}",
    )

    # Figure 4
    pop_growth_rates_year_groups(
        year=dof_year,
        save_path=f"outputs/{target_city}/City Population Percentage Gain, Coachella Valley, 1990-{dof_year}",
    )

    # Generate target city in format for ACS

    target_city_acs = f"{target_city.lower()} ca"
    target_city_acs_comma = f"{target_city.lower()}, ca"

    await age_distribution(
        client=client,
        year=str(acs_year),
        target_city=target_city_acs,
        save_path=f"outputs/{target_city}/Age Distribution, {target_city}, Rest of Coachella Valley, Rest of Riverside County, {acs_year}",
    )

    # Figure 6
    await race_group_distribution(
        client=client,
        cities=[target_city_acs_comma],
        year=str(acs_year),
        save_path=f"outputs/{target_city}/Racial Group Distribution, {target_city}, {acs_year}",
    )

    # Figure 7
    await households_with_internet(
        client=client,
        target_city=target_city,  # Doesn't need the ACS formatting
        year=str(acs_year),
        save_path=f"outputs/{target_city}/Percentage of Households with Internet, Coachella Valley, {acs_year}",
    )

    # # Table 1
    # await residence_and_work_loc(
    #     client=client,
    #     cities=[target_city_acs_comma],
    #     year=str(acs_year),
    #     save_path=f"outputs/{target_city}/Residence and Work Location TABLE.png",
    # )


@timer_async
async def income_plots(target_city: str, acs_year: int, client: ACSClient):
    cities = [
        "Coachella",
        "Cathedral City",
        "Desert Hot Springs",
        "Indian Wells",
        "Indio",
        "La Quinta",
        "Palm Desert",
        "Palm Springs",
        "Rancho Mirage",
    ]

    cities_comma = [city.lower() + ", ca" for city in cities]

    target_city_acs_comma = f"{target_city.lower()}, ca"
    # Figure 8
    await total_household_income(
        client=client,
        target_city=target_city_acs_comma.split(",")[0],
        year=str(acs_year),
        save_path=f"outputs/{target_city}/Total Household Income, Annual, {target_city}, Rest of Coachella Valley, {acs_year}",
    )

    # Figure 9
    await median_household_income(
        client=client,
        target_city=target_city_acs_comma.split(",")[0],
        year=str(acs_year),
        save_path=f"outputs/{target_city}/Median Household Income, {target_city}, Rest of Coachella Valley, {acs_year}",
    )

    # Figure 10
    await household_income_by_class(
        client=client,
        cities=cities_comma,
        target_city=target_city_acs_comma.split(",")[
            0
        ],  # This function searches on location_key, which removes the comma
        save_path=f"outputs/{target_city}/Household Income By Class, {acs_year}",
    )


@timer
def employment_plots(
    target_city: str,
    data_path: str = "data/CV_EMPL.csv",
    bls_year: int = 2022,
    edd_year: int = 2021,
):
    # Figure 14
    avg_monthly_employment(
        city=target_city,
        data_path=data_path,
        save_path=f"outputs/{target_city}/Average Monthly Total Employment, {target_city}, 2005-{edd_year}",
    )

    # Figure 15 -- Unemployment Rates US, CA, IE, City
    if target_city not in [
        "Indian Wells",
        "Rancho Mirage",
    ]:  # These cities don't have unemployment rates in BLS due to population < 25,000
        unemployment_rates(
            city=target_city,
            year=str(bls_year),
            save_path=f"outputs/{target_city}/Unemployment Rate, {target_city}, Inland Empire, California, United States, 2000-{bls_year}",
        )

    # Figure 16 -- Employment composition (new plot)
    employment_composition_pandemic_now(
        city=target_city,
        data_path=data_path,
        save_path=f"outputs/{target_city}/Employment Composition, {target_city}, Pandemic Drop to Now",
    )

    # Former Figure 19 & Figure 20 ??
    peak_to_trough_empl(
        city=target_city,
        data_path=data_path,
        save_path_abs=f"outputs/{target_city}/Change in Employment Share, Peak to Trough, {target_city}, {edd_year}",
        save_path_perc=f"outputs/{target_city}/Percent Change in Employment Share, Peak to Trough, {target_city}, {edd_year}",
    )


@timer
def taxable_sales_plots(target_city: str, data_path: str = "data/taxable_sales.csv"):
    # Figure 21
    real_nominal_sales_pc_time_series(
        city=target_city,
        data_path=data_path,
        save_path=f"outputs/{target_city}/Real and Nominal Retail Sales per Capita, {target_city}",
    )

    # Figure 22
    taxable_sales_per_capita_quarters_cv(
        data_path=data_path,
        save_path=f"outputs/{target_city}/Quarterly Taxable Sales per Capita, Coachella Valley",
    )


@timer_async
async def education_human_capital_plots(
    client: ACSClient, target_city: str, acs_year: int
):
    # Figure 25
    await human_capital_index_cv(
        client=client,
        year=str(acs_year),
        target_city=target_city.lower(),
        save_path=f"outputs/{target_city}/Human Capital Index, {target_city}, Coachella Valley, {acs_year}",
    )

    # Figure 26
    await educational_attainment_cv(
        client=client,
        year=str(acs_year),
        save_path=f"outputs/{target_city}/High School and College Attainment Rage, Coachella Valley, {acs_year}",
    )


@timer_async
async def health_insurance_plots(client: ACSClient, target_city: str, acs_year: int):
    target_city_acs_comma = f"{target_city.lower()}, ca"
    # Figure 27
    await health_insurance(
        client=client,
        city=target_city_acs_comma,
        year=str(acs_year),
        save_path=f"outputs/{target_city}/Percentage of Population with Health Insurance, {target_city}, California, United States, 2010-{acs_year}",
    )


# ------------------------------
# Main Function
# ------------------------------


async def main(
    dof_year: int = 2021,
    acs_year: int = 2019,
    bls_year: int = None,
    edd_year: int = 2021,
):
    """main generates all of the plots for the city reports

    Parameters
    ----------
    dof_year : int, optional
        Year to use to analyze DOF data, controls both graphs and filenames, by default 2021
    acs_year : int, optional
        Year to use to analyze ACS data, controls both graphs and filenames, by default 2019
    bls_year : int, optional
        Year to use to analyze BLS data, controls both graphs and filenames, by default None
    edd_year : int, optional
        Year to use to analyze EDD data, only controls filenames, by default 2021
    """
    _make_dirs()

    cities = [
        "Coachella",
        "Cathedral City",
        "Desert Hot Springs",
        "Indian Wells",
        "Indio",
        "La Quinta",
        "Palm Desert",
        "Palm Springs",
        "Rancho Mirage",
    ]
    bls_year = datetime.datetime.now().year if bls_year is None else bls_year
    acs_client = ACSClient()
    await acs_client.initialize()

    try:
        for city in cities:
            print(f"Generating plots for {city.title()}")
            print("---------------------" + "-" * len(city) + "\n")
            await demographics_plots(
                target_city=city,
                dof_year=dof_year,
                acs_year=acs_year,
                client=acs_client,
            )

            await income_plots(target_city=city, acs_year=acs_year, client=acs_client)

            employment_plots(
                target_city=city,
                data_path="data/CV_EMPL.csv",
                bls_year=bls_year,
                edd_year=edd_year,
            )

            taxable_sales_plots(target_city=city)

            await education_human_capital_plots(
                client=acs_client, target_city=city, acs_year=acs_year
            )

            await health_insurance_plots(
                client=acs_client, target_city=city, acs_year=acs_year
            )
            print("\n")
    finally:
        await acs_client.close()


if __name__ == "__main__":
    asyncio.run(main())
