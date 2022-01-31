import asyncio
import os
import time

from functools import wraps
from multiprocessing import Pool, cpu_count

from numpy import save

from demographics import (
    city_population_cv_present,
    city_population_cv_time_series,
    pop_growth_rates,
    pop_growth_rates_year_groups,
    age_distribution,
    race_group_distribution,
    households_with_internet,
    residence_and_work_loc,
)

from income import (
    total_household_income,
    median_household_income,
    household_income_by_class,
)

from employment import (
    avg_monthly_employment,
    employment_composition_pandemic_now,
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
        save_path=f"outputs/{target_city}/City Population CV {target_city}.png",
    )

    # Figure 2
    city_population_cv_time_series(
        save_path=f"outputs/{target_city}/City Population CV Time Series.png"
    )

    # Figure 3
    pop_growth_rates(
        target_city=target_city,
        save_path=f"outputs/{target_city}/Population Growth Rates {target_city} Rest of CV.png",
    )

    # Figure 4
    pop_growth_rates_year_groups(
        year=dof_year,
        save_path=f"outputs/{target_city}/Population Growth Rates Groups.png",
    )

    # Generate target city in format for ACS

    target_city_acs = f"{target_city.lower()} ca"
    target_city_acs_comma = f"{target_city.lower()}, ca"

    await age_distribution(
        client=client,
        year=str(acs_year),
        target_city=target_city_acs,
        save_path=f"outputs/{target_city}/Age Distribution {target_city}.png",
    )

    # Figure 6
    await race_group_distribution(
        client=client,
        year=str(acs_year),
        save_path=f"outputs/{target_city}/Racial Group Distribution.png",
    )

    # Figure 7
    await households_with_internet(
        client=client,
        year=str(acs_year),
        save_path=f"outputs/{target_city}/Households With Internet.png",
    )

    # Table 1
    await residence_and_work_loc(
        client=client,
        cities=[target_city_acs_comma],
        year=str(acs_year),
        save_path=f"outputs/{target_city}/Residence and Work Location TABLE.png",
    )


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
        year=str(acs_year),
        save_path=f"outputs/{target_city}/Total Household Income.png",
    )

    # Figure 9
    await median_household_income(
        client=client,
        year=str(acs_year),
        save_path=f"outputs/{target_city}/Median Household Income.png",
    )

    # Figure 10
    await household_income_by_class(
        client=client,
        cities=cities_comma,
        save_path=f"outputs/{target_city}/Household Income By Class.png",
    )


@timer
def employment_plots(target_city: str, data_path: str = "data/CV_EMPL.csv"):
    # Figure 14
    avg_monthly_employment(
        city=target_city,
        data_path=data_path,
        save_path=f"outputs/{target_city}/Average Monthly Total Employment Per Year",
    )

    # Figure 16 -- Employment composition (new plot)
    employment_composition_pandemic_now(
        city=target_city,
        data_path=data_path,
        save_path=f"outputs/{target_city}/Employment Composition Pandemic Drop to Now",
    )

    # Former Figure 19 & Figure 20 ??
    peak_to_trough_empl(
        city=target_city,
        data_path=data_path,
        save_path_abs=f"outputs/{target_city}/Change in Employment, Peak to Trough, by Sector",
        save_path_perc=f"outputs/{target_city}/% Change in Employment,  Peak to Trough, by Sector",
    )


@timer
def taxable_sales_plots(target_city: str, data_path: str = "data/taxable_sales.csv"):
    # Figure 21
    real_nominal_sales_pc_time_series(
        city=target_city,
        data_path=data_path,
        save_path=f"outputs/{target_city}/Real and Nominal Retail Sales Per Capita.png",
    )

    # Figure 22
    taxable_sales_per_capita_quarters_cv(
        data_path=data_path,
        save_path=f"outputs/{target_city}/Taxable Sales Per Capita CV.png",
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
        save_path=f"outputs/{target_city}/Human Capital Index CV.png",
    )

    # Figure 26
    await educational_attainment_cv(
        client=client,
        year=str(acs_year),
        save_path=f"outputs/{target_city}/Educatinal Attainment.png",
    )


@timer_async
async def health_insurance_plots(client: ACSClient, target_city: str, acs_year: int):
    target_city_acs_comma = f"{target_city.lower()}, ca"
    # Figure 27
    await health_insurance(
        client=client,
        city=target_city_acs_comma,
        year=str(acs_year),
        save_path=f"outputs/{target_city}/Health Insurance.png",
    )


# ------------------------------
# Main Function
# ------------------------------


async def main(dof_year: int = 2021, acs_year: int = 2019):
    _make_dirs()

    cities = [
        "Coachella",
        "Cathedral City",
        # "Desert Hot Springs",
        "Indian Wells",
        "Indio",
        "La Quinta",
        "Palm Desert",
        "Palm Springs",
        "Rancho Mirage",
    ]

    acs_client = ACSClient()
    await acs_client.initialize()

    try:
        for city in cities:
            print(f"Generating plots for {city.title()}")
            await demographics_plots(
                target_city=city,
                dof_year=dof_year,
                acs_year=acs_year,
                client=acs_client,
            )

            await income_plots(target_city=city, acs_year=acs_year, client=acs_client)

            employment_plots(target_city=city, data_path="data/CV_EMPL.csv")

            taxable_sales_plots(target_city=city)

            await education_human_capital_plots(
                client=acs_client, target_city=city, acs_year=acs_year
            )

            await health_insurance_plots(
                client=acs_client, target_city=city, acs_year=acs_year
            )
    finally:
        await acs_client.close()


if __name__ == "__main__":
    asyncio.run(main())
