import numpy as np
import pandas as pd
from pandas.core.reshape.melt import melt


def _load_msa(fname: str = "data/RIVE$HWS.xlsx", melted: bool = True):
    """Helper function to load and preprocess the data for a particular MSA"""
    # Read in the data
    df = pd.read_excel(fname, skiprows=7, skipfooter=9)
    cols = df.columns

    # Gather all of the dates into one column
    if melted:
        df = pd.melt(df, id_vars=[cols[i] for i in range(8)])
        mapper = {"variable": "time"} 
        df.rename(
            mapper=mapper,
            axis=1,
            inplace=True,
        )

    # Make sure the output is in datetime format

    if melted:
        df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%d")

    return df


def _kleinhenz_process(fname: str = "data/RIVE$HWS.xlsx"):
    """_kleinhenz_process produces the variables Dr. Kleinhenz has us use for the EDD news releases

    Parameters
    ----------
    fname : str
        Filename containing the EDD data we want to process
    """

    df = _load_msa(fname=fname, melt=False)

    # We only want a subset of columns:
    # SS-NAICS, Title, 
    # Feb-20:Jun-20, and Apr-21: (Apr 21 to last column)
    
    # titanic[["Age", "Sex"]]
    # np.r_[1:10, 15, 17, 50:100]

    indices = {df.columns.get_loc(c): c for idx, c in enumerate(df.columns)}
    cols_of_interest = [
        "Title",
        "SS-NAICS",
        "Feb-20",
        "Mar-20",
        "Apr-20",
        "May-20",
        "Jun-20",
        "Apr-21"
    ]
    idxs = [str(indices[col]) for col in cols_of_interest]
    idxs[-1] = idxs[-1] + f":{len(df.columns) + 1}"

    


if __name__ == "__main__":
    df = _load_msa()
