from pickletools import bytes4


import datetime
import glob
import os
from pyexpat import features
import pandas as pd
import requests

from bidict import bidict
from bs4 import BeautifulSoup
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile


def download_edd_data():
    base = "http://labormarketinfo.edd.ca.gov"

    main_page_uri = f"{base}/data/employment-by-industry.html"
    print(main_page_uri)

    # https://www.labormarketinfo.edd.ca.gov/file/indhist/allhws.zip
    r = requests.get(main_page_uri)
    resp = r.text
    soup = BeautifulSoup(resp, features="html.parser")

    selector = "#main_content > div > main > table > tbody > tr:nth-child(2) > td:nth-child(3) > a:nth-child(3)"

    elems = soup.select(selector)
    download_url_zip = base + elems[0].get("href")

    print("HERE")
    print([elem.get("href") for elem in elems])

    with urlopen(download_url_zip) as zipresp:
        with ZipFile(BytesIO(zipresp.read())) as zfile:
            zfile.extractall("/datatest")


def main():
    download_edd_data()


if __name__ == "__main__":
    main()
