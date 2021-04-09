import urllib.request, urllib.error, urllib.parse


def getHTML(url: str, filename: str):
    """
    Grabs the web data from a url creates a file in the working directory with the HTML code of that URL.
    """
    response = urllib.request.urlopen(url)
    webContent = response.read()

    f = open(filename, "wb")
    f.write(webContent)
    f.close


# Get the HTML file for the US Census Bureau 5-year estimates variable list

varListURL = "https://api.census.gov/data/2019/acs/acs5/variables.html"
name = "acs_var_list_5_year_2019.html"

getHTML(varListURL, name)