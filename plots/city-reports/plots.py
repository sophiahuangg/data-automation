import asyncio
import os
import time

from functools import wraps
from multiprocessing import Pool, cpu_count

from demographics import (
    city_population_cv_present,
    city_population_cv_time_series,
    pop_growth_rates,
    pop_growth_rates_year_groups,
    age_distribution,
    race_group_distribution,
    households_with_internet,
)

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
    target_city: str,
    dof_year: int,
    acs_year: int,
):
    city_population_cv_present(
        year=dof_year,
        target_city=target_city,
        save_path=f"outputs/{target_city}/City Population CV {target_city}.png",
    )

    city_population_cv_time_series(
        save_path=f"outputs/{target_city}/City Population CV Time Series.png"
    )

    pop_growth_rates(
        target_city=target_city,
        save_path=f"outputs/{target_city}/Population Growth Rates {target_city} Rest of CV.png",
    )

    pop_growth_rates_year_groups(
        year=dof_year,
        save_path=f"outputs/{target_city}/Population Growth Rates Groups.png",
    )

    client = ACSClient()

    # Generate target city in format for ACS

    target_city_acs = f"{target_city.lower()} ca"

    try:
        await client.initialize()

        await age_distribution(
            client=client,
            year=str(acs_year),
            target_city=target_city_acs,
            save_path=f"outputs/{target_city}/Age Distribution {target_city}.png",
        )

        await race_group_distribution(
            client=client,
            year=str(acs_year),
            save_path=f"outputs/{target_city}/Racial Group Distribution.png",
        )

        await households_with_internet(
            client=client,
            year=str(acs_year),
            save_path=f"outputs/{target_city}/Households With Internet.png",
        )

    finally:
        await client.close()


async def main(dof_year: int = 2021, acs_year: int = 2019):
    _make_dirs()

    class DemographicsPlots:
        def __init__(self, dof_year: int, acs_year: int):
            self.dof_year = dof_year
            self.acs_year = acs_year

        def __call__(self, city):
            return demographics_plots(
                dof_year=self.dof_year, acs_year=self.acs_year, target_city=city
            )

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
        await demographics_plots(target_city=city, dof_year=dof_year, acs_year=acs_year)


if __name__ == "__main__":
    asyncio.run(main())
