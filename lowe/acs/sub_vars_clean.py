import requests
import json
import re

response = requests.get(
    "https://api.census.gov/data/2019/acs/acs5/subject/variables.json"
)

data = response.json()
for v in data.values():
    for elem in v:
        val = v[elem]
        val["label"] = re.sub("!!", " ", val["label"])
        # print(val['label'])

with open("acs_subjects_2019.json", "w") as output:
    json.dump(data["variables"], output)

"""
Output file format:
{
    NAME : {
        "label": "xx",
        "concept": "xx",
        "predicateType": "xx",
        "group": "xx",
        "limit": 2,
        "attributes": "S0804_C04_068EA,S0804_C04_068M,S0804_C04_068MA"
    }
}

filename: acs_subjects_2019.json
"""
