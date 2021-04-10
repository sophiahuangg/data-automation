from bs4 import BeautifulSoup
import requests

with open("acs_var_list_5_year_2019.html") as html_file:
    # Do NOT print the contents of this. The html file is > 135k lines long.
    # You may have to type pip3 install lxml
    soup = BeautifulSoup(html_file, "lxml")

table = soup.find("tbody")

rows = table.find_all("tr")

Name = []
Label = []
Concept = []

for row in rows[0:6]:
    # Get the column names
    name = row.td.a["name"]
    Name.append(name)

    cols = row.find_all("td")
    label = cols[1]
    concept = cols[2]

    Label.append(label)
    Concept.append(concept)
