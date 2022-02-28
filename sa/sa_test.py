import datetime
import json
import pandas as pd

from lowe.bls.BLSClient import BLSClient
from statsmodels.tsa.x13 import x13_arima_analysis

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources


def main():
    client = BLSClient()
    with pkg_resources.open_text("lowe.bls", "bls_series.json") as f:
        bls_series = json.load(f)

    ur_codes = bls_series["Unemployment Rate"]

    codes = [ur_codes["US"], ur_codes["CA"], ur_codes["IE"], ur_codes["Indio"]]
    names = ["ur_us", "ur_ca", "ur_ie", f"ur_Indio"]

    # Initialize a BLS client and get the data
    client = BLSClient()

    data_raw = client.get_bls(
        seriesid=codes,
        startyear="2005",
        endyear="2022",
        valuename=names,
    )

    # Clean the data and join the datasets together
    df = data_raw[0].drop(columns=["year", "latest"])
    df["time"] = df["time"].apply(lambda x: datetime.datetime.strftime(x, "%b %Y"))

    for new_df in data_raw[1:]:
        new_df.drop(columns=["year", "latest"], inplace=True)
        new_df["time"] = new_df["time"].apply(
            lambda x: datetime.datetime.strftime(x, "%b %Y")
        )
        df = df.merge(new_df, on="time")

    for col in df.columns:
        if "ur" in col:
            df[col] = df[col].astype(float)

    df_sa_test = df.set_index("time")
    df_sa_test.index = pd.to_datetime(df_sa_test.index)

    sa_test = x13_arima_analysis(
        endog=df_sa_test["ur_ca"],
        log=False,
        trading=False,
        print_stdout=True,
        x12path="./x13as"
    )

    return df_sa_test


if __name__ == "__main__":
    test = main()
    print(test)
