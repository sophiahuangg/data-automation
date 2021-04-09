from bs4 import BeautifulSoup
import requests

with open("acs_var_list_5_year_2019.html") as html_file:
    # Do NOT print the contents of this. The html file is > 135k lines long.
    soup = BeautifulSoup(html_file, "lxml")