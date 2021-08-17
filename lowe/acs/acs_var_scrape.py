from bs4 import BeautifulSoup
import requests
import json
import re

with open("acs_var_list_5_year_2019.html") as html_file:
    # Do NOT print the contents of this. The html file is > 135k lines long.
    # You may have to type pip3 install lxml
    soup = BeautifulSoup(html_file, "lxml")

table = soup.find("tbody")

rows = table.find_all("tr")

Name = []
Label = []
Concept = []

for row in rows:  # Loop over the rows of the table
    # Get the column detailing the series ID and append it to the Name list
    name = row.td.a["name"]
    Name.append(name)

    cols = row.find_all("td")  # Find all columns in the row
    label = cols[1].text  # Get the label column
    concept = cols[2].text  # Get the concept column

    # Append the label and concept fields to the corresponding lists

    Label.append(label)
    Concept.append(concept)

# Initialize output dictionary
out = {}

for i in range(len(Name)):
    Label[i] = re.sub("!!", " ", Label[i])  # Replace the !! in label with a space
    out[Name[i]] = {
        "Concept": Concept[i],
        "Label": Label[i],
    }  # Add items to output dictionary

with open("acs_vars_2019.json", "w") as outFile:
    json.dump(out, outFile)  # Write the output dictionary to a json file

"""
Output file format:
{
    NAME : {
        CONCEPT: alkjhvcsuiofhso8iaf,
        LABEL: aoihjfoiwhgo8isgigo
    }
}

filename: acs_vars.json
"""
