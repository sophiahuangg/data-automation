import requests
from bs4 import BeautifulSoup

def get_data():
    base_url = "https://www.dof.ca.gov/Forecasting/Demographics/Estimates/"
    r = requests.get(base_url, verify=False)
    resp = r.text
    soup = BeautifulSoup(resp, features="html.parser")

    elems = soup.select('a[href*="E-4"], a[href*="e-4"]')
    hrefs = [base_url + elem.get('href') for elem in elems]
    print(hrefs)
    for url in hrefs:
        # Get the link for the Excel file
        r = requests.get(url, verify=False)
        soup = BeautifulSoup(r.text, features="html.parser")
        link_additions = soup.select('a[href$=".xlsx"], a[href$=".xls"]')
        url += link_additions[0].get('href')

        # Generate the output filename from the URL
        url_split = url.split("/")
        fname = 

        # Get the Excel file
        xl = requests.get(url, verify=False)

def main():
    pass


if __name__ == "__main__":
    get_data()
