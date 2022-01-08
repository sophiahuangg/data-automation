from demographics import city_population_cv_present


def demographics_plots(
    year: int,
    target_city: str,
):
    city_population_cv_present(
        year=year,
        target_city=target_city,
        save_path=f"outputs/City Population CV {target_city}.png",
    )


def main():
    demographics_plots(year=2021, target_city="Desert Hot Springs")


if __name__ == "__main__":
    main()
